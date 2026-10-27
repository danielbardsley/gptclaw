import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ApiError, NotesClient } from '../api/client';
import type { Note, NotesPage } from '../api/contract';

const ink = '#232C32';
const muted = '#58635D';
const blue = '#243FBD';
const api = new NotesClient();
type Draft = { id?: string; title: string; body: string; original: string };
const signature = (title: string, body: string) =>
  JSON.stringify([title, body]);

function Action({
  label,
  onPress,
  secondary = false,
  disabled = false,
}: {
  label: string;
  onPress: () => void;
  secondary?: boolean;
  disabled?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        s.action,
        secondary ? s.secondary : s.primary,
        pressed && s.pressed,
        disabled && s.disabled,
      ]}
    >
      <Text style={[s.actionText, secondary && s.secondaryText]}>{label}</Text>
    </Pressable>
  );
}

export function Notebook({ client = api }: { client?: NotesClient }) {
  const [page, setPage] = useState<NotesPage>({
    items: [],
    total: 0,
    limit: 20,
    offset: 0,
  });
  const [draft, setDraft] = useState<Draft | null>(null);
  const [busy, setBusy] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uncertain, setUncertain] = useState(false);
  const [saved, setSaved] = useState(false);
  const [readback, setReadback] = useState('');
  const alive = useRef(true);
  const pending = useRef(true);
  const dirty =
    draft !== null && signature(draft.title, draft.body) !== draft.original;

  const perform = useCallback(async (work: () => Promise<void>) => {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      await work();
    } catch (failure) {
      if (alive.current) {
        setError(
          failure instanceof ApiError
            ? failure.message
            : 'Something interrupted your notebook. Refresh to try again.',
        );
        if (failure instanceof ApiError && failure.kind === 'uncertain')
          setUncertain(true);
      }
    } finally {
      pending.current = false;
      if (alive.current) {
        setBusy(false);
        setLoading(false);
      }
    }
  }, []);
  const refresh = useCallback(
    async (offset = 0) => {
      let result = await client.list(offset);
      if (offset > 0 && result.items.length === 0 && result.total > 0) {
        result = await client.list(Math.max(0, offset - result.limit));
      }
      if (alive.current) {
        setPage(result);
        setUncertain(false);
      }
    },
    [client],
  );

  useEffect(() => {
    alive.current = true;
    let active = true;
    void client
      .list()
      .then((result) => {
        if (active) setPage(result);
      })
      .catch((failure) => {
        if (active)
          setError(
            failure instanceof ApiError
              ? failure.message
              : 'Something interrupted your notebook. Refresh to try again.',
          );
      })
      .finally(() => {
        if (active) {
          pending.current = false;
          setBusy(false);
          setLoading(false);
        }
      });
    return () => {
      active = false;
      alive.current = false;
    };
  }, [client]);

  async function recover() {
    await perform(async () => {
      if (!uncertain) {
        await refresh(page.offset);
        return;
      }
      const first = await client.list(0);
      const offset =
        Math.floor(Math.max(0, first.total - 1) / first.limit) * first.limit;
      const latest = offset ? await client.list(offset) : first;
      if (alive.current) {
        setPage(latest);
        setReadback(
          latest.items
            .map((item) => item.title + ' — ' + item.preview)
            .join('\n') || 'No saved notes found.',
        );
        setUncertain(false);
      }
    });
  }

  function leave() {
    if (busy) return;
    if (dirty)
      Alert.alert(
        'Keep this thought?',
        'Your unsaved edits will be lost if you leave.',
        [
          { text: 'Keep editing', style: 'cancel' },
          {
            text: 'Discard edits',
            style: 'destructive',
            onPress: () => {
              setDraft(null);
              setError('');
              setSaved(false);
            },
          },
        ],
      );
    else {
      setDraft(null);
      setError('');
      setSaved(false);
    }
  }
  async function save() {
    if (!draft || uncertain) return;
    const input = { title: draft.title.trim(), body: draft.body };
    if (
      !input.title ||
      input.title.length > 120 ||
      input.body.length > 10_000
    ) {
      setError(
        'Add a title of 1–120 characters. Notes can hold up to 10,000 characters.',
      );
      return;
    }
    await perform(async () => {
      const note = await client.save(input, draft.id);
      if (!alive.current) return;
      setDraft({
        id: note.id,
        title: note.title,
        body: note.body ?? '',
        original: signature(note.title, note.body ?? ''),
      });
      setSaved(true);
      await refresh();
    });
  }
  function remove() {
    if (!draft?.id || busy) return;
    const id = draft.id;
    Alert.alert(
      'Delete this note?',
      'This removes the saved note from your notebook.',
      [
        { text: 'Keep note', style: 'cancel' },
        {
          text: 'Delete note',
          style: 'destructive',
          onPress: () =>
            void perform(async () => {
              await client.remove(id);
              if (alive.current) {
                setDraft(null);
                setSaved(false);
              }
              await refresh();
            }),
        },
      ],
    );
  }
  const open = (id: string) =>
    void perform(async () => {
      const note: Note = await client.get(id);
      if (alive.current) {
        setDraft({
          id: note.id,
          title: note.title,
          body: note.body ?? '',
          original: signature(note.title, note.body ?? ''),
        });
        setSaved(false);
        setUncertain(false);
      }
    });
  const newNote = () => {
    if (!busy) {
      setDraft({ title: '', body: '', original: signature('', '') });
      setReadback('');
      setSaved(false);
      setError('');
      setUncertain(false);
    }
  };

  return (
    <SafeAreaView style={s.screen}>
      <KeyboardAvoidingView
        style={s.fill}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={s.content}
          keyboardShouldPersistTaps="handled"
          automaticallyAdjustKeyboardInsets
        >
          <View style={s.masthead}>
            <Text style={s.wordmark}>FIELDNOTES</Text>
            <Text style={s.edition}>A LITTLE SPACE TO THINK</Text>
          </View>
          {draft ? (
            <>
              <Action
                label="Back to notebook"
                onPress={leave}
                secondary
                disabled={busy}
              />
              <View style={s.editorHeading}>
                <Text style={s.eyebrow}>
                  {draft.id ? 'YOUR NOTE' : 'A FRESH PAGE'}
                </Text>
                <Text accessibilityLiveRegion="polite" style={s.saveState}>
                  {busy
                    ? 'Working…'
                    : dirty
                      ? 'Unsaved changes'
                      : saved
                        ? 'Saved to your notebook'
                        : 'Ready to write'}
                </Text>
              </View>
              <Text style={s.inputLabel}>Title</Text>
              <TextInput
                accessibilityLabel="Note title"
                placeholder="Give this thought a title"
                placeholderTextColor={muted}
                value={draft.title}
                maxLength={120}
                onChangeText={(title) => {
                  setDraft({ ...draft, title });
                  setSaved(false);
                }}
                style={s.titleInput}
                editable={!busy}
              />
              <View style={s.rule} />
              <Text style={s.inputLabel}>Your words</Text>
              <TextInput
                accessibilityLabel="Note body"
                placeholder="An idea, a small discovery, a thing to remember…"
                placeholderTextColor={muted}
                value={draft.body}
                onChangeText={(body) => {
                  setDraft({ ...draft, body });
                  setSaved(false);
                }}
                multiline
                textAlignVertical="top"
                maxLength={10_000}
                style={s.bodyInput}
                editable={!busy}
              />
              <Text style={s.caption}>
                {draft.body.length.toLocaleString()} / 10,000 characters ·
                Shared private notebook
              </Text>
            </>
          ) : (
            <>
              <View style={s.headingRow}>
                <Text accessibilityRole="header" style={s.hero}>
                  Make room{'\n'}for a thought.
                </Text>
                <View style={s.number}>
                  <Text style={s.numberText}>
                    {String(page.total).padStart(2, '0')}
                  </Text>
                  <Text style={s.numberLabel}>NOTES</Text>
                </View>
              </View>
              <Text style={s.subtitle}>
                Small discoveries. Unfinished ideas.{'\n'}Keep the things worth
                coming back to.
              </Text>
              <Action
                label="＋ Write a note"
                onPress={newNote}
                disabled={busy}
              />
              <View style={s.sectionLine}>
                <Text style={s.eyebrow}>YOUR COLLECTION</Text>
                <Text style={s.caption}>A PLACE FOR YOUR IDEAS</Text>
              </View>
            </>
          )}
          {error ? (
            <View accessibilityRole="alert" style={s.notice}>
              <Text accessibilityLiveRegion="assertive" style={s.errorTitle}>
                {uncertain
                  ? 'Let’s check what was saved.'
                  : 'A small interruption.'}
              </Text>
              <Text style={s.errorBody}>{error}</Text>
              <Action
                label={uncertain ? 'Refresh saved notes' : 'Refresh notebook'}
                onPress={() => void recover()}
                secondary
                disabled={busy}
              />
              {uncertain ? (
                <Text style={s.caption}>
                  Your draft is still here. Review the saved collection before
                  repeating a change.
                </Text>
              ) : null}
            </View>
          ) : null}
          {draft && readback ? (
            <View style={s.notice}>
              <Text style={s.errorTitle}>Latest saved notes</Text>
              <Text style={s.errorBody}>{readback}</Text>
              <Text style={s.caption}>
                Compare these saved records with your draft before trying the
                change again.
              </Text>
            </View>
          ) : null}
          {loading || busy ? (
            <ActivityIndicator
              accessibilityLabel="Loading notebook"
              color={blue}
              style={s.loader}
            />
          ) : null}
          {draft ? (
            <View style={s.editorActions}>
              <Action
                label={busy ? 'Working…' : 'Save note'}
                onPress={() => void save()}
                disabled={busy || uncertain || !dirty}
              />
              {draft.id ? (
                <Action
                  label="Delete note"
                  onPress={remove}
                  secondary
                  disabled={busy || uncertain}
                />
              ) : null}
            </View>
          ) : (
            <>
              {!loading && !error && page.items.length === 0 ? (
                <View style={s.empty}>
                  <Text style={s.emptyMark}>✳</Text>
                  <Text accessibilityRole="header" style={s.emptyTitle}>
                    Every notebook starts{'\n'}with a blank page.
                  </Text>
                  <Text style={s.emptyBody}>
                    Capture your first thought. It’ll be here when you return.
                  </Text>
                </View>
              ) : null}
              {page.items.map((note, index) => (
                <Pressable
                  key={note.id}
                  accessibilityRole="button"
                  accessibilityLabel={`Open note: ${note.title}`}
                  onPress={() => open(note.id)}
                  disabled={busy}
                  style={({ pressed }) => [
                    s.card,
                    index % 3 === 0 && s.featured,
                    pressed && s.pressed,
                  ]}
                >
                  <View style={s.cardMeta}>
                    <Text style={s.eyebrow}>
                      NOTE {String(page.offset + index + 1).padStart(2, '0')}
                    </Text>
                    <Text style={s.arrow}>↗</Text>
                  </View>
                  <Text accessibilityRole="header" style={s.cardTitle}>
                    {note.title}
                  </Text>
                  <Text style={s.preview}>
                    {note.preview || 'A little thought, safely kept.'}
                  </Text>
                  <View style={s.cardRule} />
                </Pressable>
              ))}
              {page.total > page.limit ? (
                <View style={s.pagination}>
                  <Action
                    label="Previous page"
                    onPress={() =>
                      void perform(() =>
                        refresh(Math.max(0, page.offset - page.limit)),
                      )
                    }
                    secondary
                    disabled={busy || page.offset === 0}
                  />
                  <Text style={s.caption}>
                    Page {Math.floor(page.offset / page.limit) + 1}
                  </Text>
                  <Action
                    label="Next page"
                    onPress={() =>
                      void perform(() => refresh(page.offset + page.limit))
                    }
                    secondary
                    disabled={busy || page.offset + page.limit >= page.total}
                  />
                </View>
              ) : null}
              <Action
                label="Refresh notebook"
                onPress={() => void perform(() => refresh(page.offset))}
                secondary
                disabled={busy}
              />
              <View style={s.footer}>
                <View style={s.rule} />
                <Text style={s.caption}>
                  THOUGHTFULLY KEPT. PRIVATELY CONNECTED.
                </Text>
                <Text style={s.footerNote}>
                  Synthetic shared notes · Development only{'\n'}Saved notes
                  stay here when you return.
                </Text>
              </View>
            </>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  fill: { flex: 1 },
  screen: { flex: 1, backgroundColor: '#F7F4EC' },
  content: { padding: 24, gap: 20, paddingBottom: 48 },
  masthead: {
    gap: 6,
    paddingVertical: 14,
    borderBottomWidth: 2,
    borderColor: ink,
  },
  wordmark: { color: ink, letterSpacing: 4, fontSize: 15, fontWeight: '800' },
  edition: { color: muted, fontSize: 10, letterSpacing: 1.5 },
  headingRow: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'flex-end',
    paddingTop: 22,
  },
  hero: {
    flex: 1,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    color: ink,
    fontSize: 43,
    lineHeight: 49,
    letterSpacing: -1.5,
  },
  number: {
    backgroundColor: '#E6EACA',
    borderRadius: 50,
    padding: 16,
    alignItems: 'center',
    gap: 3,
  },
  numberText: { fontSize: 28, color: ink, fontWeight: '500' },
  numberLabel: { color: ink, fontSize: 9, letterSpacing: 1.5 },
  subtitle: { color: muted, fontSize: 16, lineHeight: 25 },
  action: {
    minHeight: 48,
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primary: { backgroundColor: blue },
  secondary: {
    borderWidth: 1,
    borderColor: '#B7BDB2',
    backgroundColor: '#F7F4EC',
  },
  actionText: { color: '#FFFFFF', fontSize: 16, fontWeight: '600' },
  secondaryText: { color: ink },
  pressed: { opacity: 0.75 },
  disabled: { opacity: 0.5 },
  sectionLine: { gap: 8, paddingTop: 24, paddingBottom: 4 },
  eyebrow: { fontSize: 11, fontWeight: '700', letterSpacing: 2, color: muted },
  caption: { fontSize: 11, lineHeight: 18, color: muted },
  card: {
    backgroundColor: '#FFFDF7',
    padding: 22,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#D5D8CB',
    gap: 14,
    minHeight: 160,
  },
  featured: {
    backgroundColor: '#E6EACA',
    borderColor: '#CFD6B6',
    borderTopRightRadius: 36,
  },
  cardMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  arrow: { color: ink, fontSize: 22 },
  cardTitle: {
    color: ink,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    fontSize: 27,
    lineHeight: 34,
  },
  preview: { fontSize: 15, lineHeight: 24, color: muted },
  cardRule: { height: 1, backgroundColor: '#C4C9B9', width: 36 },
  empty: {
    paddingVertical: 36,
    paddingHorizontal: 14,
    alignItems: 'center',
    gap: 18,
  },
  emptyMark: { fontSize: 48, color: blue },
  emptyTitle: {
    color: ink,
    fontSize: 27,
    lineHeight: 34,
    textAlign: 'center',
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },
  emptyBody: {
    textAlign: 'center',
    color: muted,
    fontSize: 16,
    lineHeight: 24,
  },
  loader: { padding: 16 },
  editorHeading: { gap: 10, paddingTop: 10 },
  saveState: { color: muted, fontSize: 13 },
  inputLabel: {
    color: muted,
    fontSize: 12,
    letterSpacing: 1,
    fontWeight: '600',
  },
  titleInput: {
    minHeight: 60,
    color: ink,
    fontSize: 30,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    paddingVertical: 10,
  },
  bodyInput: {
    minHeight: 280,
    color: ink,
    fontSize: 18,
    lineHeight: 30,
    paddingVertical: 12,
  },
  editorActions: { gap: 12 },
  rule: { height: 1, backgroundColor: '#C4C9B9', marginVertical: 4 },
  notice: {
    backgroundColor: '#F1E5D5',
    borderLeftWidth: 3,
    borderColor: '#79532D',
    padding: 18,
    gap: 14,
  },
  errorTitle: { color: ink, fontSize: 18, fontWeight: '600' },
  errorBody: { color: '#644827', fontSize: 15, lineHeight: 24 },
  pagination: { gap: 12 },
  footer: { gap: 12, paddingTop: 22 },
  footerNote: { color: muted, fontSize: 12, lineHeight: 20 },
});
