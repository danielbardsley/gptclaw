#!/usr/bin/env python3
"""Enumerate and verify exact template releases in task-owned disposable roots."""
import argparse
import importlib.util
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import private_apps as app
import project_templates as templates


def matrix():
    _, releases = templates.catalogue()
    newest = {}
    for key in releases:
        if key[0] not in newest or tuple(map(int, key[1].split('.'))) > tuple(map(int, newest[key[0]].split('.'))):
            newest[key[0]] = key[1]
    result = []
    for (name, version), (release, contents) in sorted(releases.items()):
        quality = 'quality.json' in contents
        if version == newest[name]:
            app.need(quality, 'template-policy')
        result.append({'id': name, 'version': version, 'digest': release['digest'],
                       'provider': release['provider'], 'checks': 'full' if quality else 'historical-generation',
                       'reason': 'Current quality-enabled release' if quality else 'Superseded exact release; preserve integrity and generation compatibility',
                       'native_device': 'pending separate physical acceptance' if 'expo' in name else 'not applicable'})
    return result


def run(selected, engine, execute=False):
    result = []
    token = uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix='gptclaw-qlt-'+token+'-') as temp:
        base = Path(temp)
        # The temp root is created exclusively here; all generated children belong to this run.
        app.PROJECTS = base
        app.STORE = base/'.gptclaw-runtime/v1'
        for cell in selected:
            slug = 'quality-'+cell['id'][:20]+'-'+cell['version'].replace('.', '-')
            root = Path(app.create(slug, template=cell['id'], template_version=cell['version'])['root'])
            report = {**cell, 'generation': 'passed', 'runtime': 'not run', 'cleanup': 'owned temporary fixture'}
            if cell['checks'] == 'full':
                spec = importlib.util.spec_from_file_location('quality_fixture_'+uuid.uuid4().hex, root/'checks/gptclaw_quality.py')
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                c = module.config(root)
                module.policy(root)
                module.workflow_policy(module.read_json(root/'.github/workflows/quality.yml'))
                module.updater_policy(module.read_json(root/'.github/dependabot.yml'), c)
                report['metadata'] = 'passed'
                if execute:
                    report['quality'] = module.run_quality(root, 'verify', engine)
                    report['runtime'] = 'passed'
                    try:
                        report['measurements'] = module.collect_performance(root)
                    except module.GateError:
                        report['measurements'] = {'state': 'not applicable', 'reason': 'No measured runtime or bundle metrics for this adapter'}
                    report['negative_checks'] = negative_checks(root, module, engine, c)
            result.append(report)
            print(json.dumps(report), flush=True)
    return {'state': 'passed', 'vantage': 'local generated fixtures', 'cells': result,
            'cleanup': 'completed for owned temporary roots; no managed targets'}


def negative_checks(root, module, engine, c):
    results = []; runner = module.Containers(root, engine, c)
    baseline = module.source_snapshot(root)
    database = any((module.relative(root, v['root'])/'migrations').is_dir() for v in c['components'].values())
    def reject(name, component, gate):
        try:
            if gate == 'test' and component['stack'] == 'python' and database:
                try:
                    runner.execute([sys.executable, str(root/c['integration']), '--engine', engine], root, 2400)
                finally:
                    runner.cleanup_integrations()
            else:
                runner.run(name, component, component['commands'][gate], network=False)
        except module.GateError:
            results.append({'component': name, 'gate': gate, 'injected_fault': 'rejected'})
        else:
            raise AssertionError('Injected fault passed '+name+'/'+gate)
    try:
        for name, component in c['components'].items():
            home = module.relative(root, component['root'], True)
            python = component['stack'] == 'python'
            if python:
                target = home/'src/fastapi_app/settings.py'
                faults = [('lint', '\nqlt_unused= 1\n'), ('typecheck', '\nqlt_type_failure: int = "wrong"\n'), ('build', '\ndef qlt_broken(\n')]
                formatting = '\nimport  os  as qlt_unused\n'
            else:
                target = next(iter(sorted((home/'app').glob('*.tsx'))), None) if (home/'app').is_dir() else next(iter(sorted((home/'src').rglob('*.tsx'))), home/'src/app.ts')
                faults = [('lint', '\nconst qltUnused = 1;\n'), ('typecheck', '\nexport const qltTypeFailure: number = "wrong";\n'), ('build', '\nexport const qltBroken = ;\n')]
                formatting = '\nconst qltUnused={value:1}\n'
            original = target.read_bytes()
            try:
                for gate, fault in faults:
                    target.write_bytes(original+fault.encode());reject(name, component, gate)
                target.write_bytes(original+formatting.encode())
                runner.run(name, component, component['commands']['format'], network=False)
                reject(name, component, 'lint')
                results.append({'component': name, 'gate': 'format', 'behavior': 'corrected formatting; semantic lint fault remains'})
            finally:
                target.write_bytes(original)
            test = next(iter(sorted((home/'tests').glob('test_*.py'))), None) if python else next(iter(sorted((home/'tests').glob('*.test.*'))), None)
            module.need(test is not None, 'Missing test fault target')
            original = test.read_bytes()
            if python:
                fault = '\n\ndef test_qlt_deliberate_failure() -> None:\n    """Reject an intentional synthetic test defect."""\n    assert str(1) == str(2), "Synthetic QLT test failure"\n'
            elif 'expo' in c['template']:
                fault = '\ntest("QLT deliberate failure", () => { expect(1).toBe(2); });\n'
            else:
                fault = '\nimport { test as qltTest } from "node:test";\nqltTest("QLT deliberate failure", () => { throw new Error("Synthetic QLT test failure"); });\n'
            try:
                test.write_bytes(original+fault.encode());reject(name, component, 'test')
            finally:
                test.write_bytes(original)
        module.need(baseline == module.source_snapshot(root), 'Negative trials modified unrelated fixture source')
    finally:
        runner.close()
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--execute', action='store_true', help='Run generated-container quality and integration gates')
    parser.add_argument('--template', help='Exact template family; never a moving latest selector')
    parser.add_argument('--version')
    parser.add_argument('--engine', choices=['podman', 'docker'], default='podman')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--github-output', type=Path, help='Append a validated dynamic CI matrix during --list')
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    cells = matrix()
    if args.template:
        app.need(args.version is not None, 'template-policy')
        cells = [v for v in cells if (v['id'], v['version']) == (args.template, args.version)]
    app.need(bool(cells), 'template-policy')
    if args.list:
        if args.github_output:
            payload={'include':[{'template':v['id'],'version':v['version']} for v in cells if v['checks']=='full']}
            with args.github_output.open('a') as output: output.write('matrix='+json.dumps(payload,separators=(',',':'))+'\n')
        print(json.dumps(cells, indent=2)); return
    result = run(cells, args.engine, args.execute)
    if args.output:
        with args.output.open('x') as output:
            output.write(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
