#!/usr/bin/env python3
"""Generate the exact grouped release and run its portable real-container checks."""
import argparse
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps
import project_groups as groups


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--engine',choices=['docker','podman'],default='docker')
    parser.add_argument('--reuse-node-image');parser.add_argument('--reuse-api-image')
    args=parser.parse_args()
    base=Path(args.directory).absolute();base.mkdir(mode=0o700)
    app.PROJECTS=base;app.STORE=base/'.gptclaw-runtime/v1'
    root=Path(app.create('notes-check',template='notes',template_version='1.2.0')['root'])
    value=app.target(root)[1]
    with groups.scope(root,value) as children:
        before={name:deps.context(path)['hashes'] for name,(path,_) in children.items()}
    argv=[sys.executable,str(root/'checks/verify.py'),'--engine',args.engine]
    for field in ('reuse_node_image','reuse_api_image'):
        if getattr(args,field):argv+=['--'+field.replace('_','-'),getattr(args,field)]
    subprocess.run(argv,check=True,timeout=1200)
    with groups.scope(root,value) as children:
        assert before=={name:deps.context(path)['hashes'] for name,(path,_) in children.items()}
    import json
    receipt=json.loads((root/'checks/output/receipt.json').read_text())
    image=receipt['images']['api']
    def gate(action):
        result=subprocess.run([args.engine,'run','--rm','--user',str(__import__('os').getuid())+':'+str(__import__('os').getgid()),
            *(['--userns=keep-id'] if args.engine=='podman' else []), '--memory=1536m','--cpus=1','--pids-limit=256',
            '--cap-drop=all','--security-opt=no-new-privileges','--volume',str(root/'api')+':/workspace:rw','--workdir','/workspace',
            '--env','PYTHONPATH=/workspace/src','--env','GPTCLAW_PROJECT_ID=notes-check','--env','PYTHONDONTWRITEBYTECODE=1',
            image,'/workspace/.venv/bin/python','scripts/quality.py',action],capture_output=True,text=True,timeout=300)
        assert result.returncode != 0, 'Seeded defect passed '+action
    faults=[('lint','src/fastapi_app/services/notes.py',lambda text:text+'\nunused= 1\n'),
            ('typecheck','src/fastapi_app/services/notes.py',lambda text:text.replace('return self._notes[note_id].model_copy(deep=True)','return 7')),
            ('test','src/fastapi_app/services/notes.py',lambda text:text.replace('Note(id=uuid4(), **body.model_dump())','Note(id=uuid4(), title="broken", body=body.body)')),
            ('security','src/fastapi_app/services/notes.py',lambda text:text+'\nimport subprocess\nsubprocess.run("echo synthetic", shell=True)\n'),
            ('build','src/fastapi_app/main.py',lambda text:'import nonexistent_synthetic_module\n'+text)]
    for action,name,mutate in faults:
        path=root/'api'/name;before_source=path.read_bytes()
        try:path.write_text(mutate(before_source.decode()));gate(action)
        finally:path.write_bytes(before_source)
        print('Notes seeded defect rejected by '+action,flush=True)
    uncovered=root/'api/src/fastapi_app/services/uncovered.py'
    try:
        uncovered.write_text('"""Synthetic uncovered critical module."""\n'+''.join(f'def branch_{i}(value: int) -> int:\n    if value:\n        return value\n    return 0\n\n' for i in range(100)))
        gate('test')
    finally:uncovered.unlink()
    print('Notes insufficient critical coverage rejected',flush=True)
    # Restore a positive covered report after deliberate coverage failure.
    subprocess.run([args.engine,'run','--rm','--user',str(__import__('os').getuid())+':'+str(__import__('os').getgid()),
        *(['--userns=keep-id'] if args.engine=='podman' else []), '--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all',
        '--security-opt=no-new-privileges','--volume',str(root/'api')+':/workspace:rw','--workdir','/workspace',
        '--env','PYTHONPATH=/workspace/src','--env','GPTCLAW_PROJECT_ID=notes-check',image,'/workspace/.venv/bin/python','scripts/quality.py','test'],check=True,timeout=300,stdout=subprocess.DEVNULL)
    print('Exact grouped generation, frozen source/locks and full container/browser checks passed.')


if __name__=='__main__':main()
