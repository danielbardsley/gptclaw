import { Alert } from 'react-native';
import {
  act,
  fireEvent,
  render,
  screen,
  userEvent,
  waitFor,
} from '@testing-library/react-native';
import { Notebook } from '../src/components/Notebook';
import { ApiError, NotesClient } from '../src/api/client';

const note = {
  id: 'one',
  title: 'A small discovery',
  body: 'Keep this thought.',
};
const page = {
  items: [{ id: note.id, title: note.title, preview: note.body }],
  total: 1,
  limit: 20,
  offset: 0,
};
function mockClient() {
  return {
    list: jest.fn().mockResolvedValue(page),
    get: jest.fn().mockResolvedValue(note),
    save: jest.fn().mockResolvedValue(note),
    remove: jest.fn().mockResolvedValue(undefined),
  };
}
async function enterText(
  target: ReturnType<typeof screen.getByLabelText>,
  value: string,
) {
  await fireEvent.changeText(target, String(target.props.value) + value);
}
function user() {
  return userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
}
beforeEach(() => jest.useFakeTimers());
afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
  jest.restoreAllMocks();
});

test('loads persisted notes, opens and updates the full record', async () => {
  const client = mockClient();
  const actions = user();
  await render(<Notebook client={client as unknown as NotesClient} />);
  await screen.findByText(note.title);
  await actions.press(
    screen.getByRole('button', { name: `Open note: ${note.title}` }),
  );
  expect(screen.getByLabelText('Note body').props.value).toBe(note.body);
  await enterText(screen.getByLabelText('Note body'), ' More.');
  await actions.press(screen.getByRole('button', { name: 'Save note' }));
  expect(client.save).toHaveBeenCalledWith(
    { title: note.title, body: note.body + ' More.' },
    'one',
  );
  expect(screen.getByText('Saved to your notebook')).toBeTruthy();
  await actions.press(screen.getByRole('button', { name: 'Back to notebook' }));
  expect(screen.getByText('YOUR COLLECTION')).toBeTruthy();
});

test('empty state, title validation, creation and delete cancellation/confirmation', async () => {
  const client = mockClient();
  client.list.mockResolvedValue({ items: [], total: 0, limit: 20, offset: 0 });
  const actions = user();
  const alert = jest.spyOn(Alert, 'alert');
  await render(<Notebook client={client as unknown as NotesClient} />);
  await screen.findByText(/Every notebook starts/);
  await actions.press(screen.getByRole('button', { name: '＋ Write a note' }));
  await enterText(screen.getByLabelText('Note body'), 'Draft');
  await actions.press(screen.getByRole('button', { name: 'Save note' }));
  expect(client.save).not.toHaveBeenCalled();
  expect(screen.getByText(/Add a title/)).toBeTruthy();
  await enterText(screen.getByLabelText('Note title'), 'A small discovery');
  await actions.press(screen.getByRole('button', { name: 'Save note' }));
  expect(client.save).toHaveBeenCalledWith(
    { title: note.title, body: 'Draft' },
    undefined,
  );
  await actions.press(screen.getByRole('button', { name: 'Delete note' }));
  expect(client.remove).not.toHaveBeenCalled();
  expect(screen.getByLabelText('Note body').props.value).toBe(note.body);
  const buttons = alert.mock.calls.at(-1)?.[2];
  const confirmed = buttons?.find((button) => button.text === 'Delete note');
  await act(async () => {
    confirmed?.onPress?.();
  });
  await waitFor(() => expect(client.remove).toHaveBeenCalledWith('one'));
  await screen.findByText(/Every notebook starts/);
});

test('uncertain save retains the draft and blocks write retry until explicit refresh', async () => {
  const client = mockClient();
  client.save.mockRejectedValueOnce(new ApiError('uncertain'));
  const actions = user();
  await render(<Notebook client={client as unknown as NotesClient} />);
  await screen.findByText(note.title);
  await actions.press(
    screen.getByRole('button', { name: `Open note: ${note.title}` }),
  );
  await enterText(screen.getByLabelText('Note body'), ' Offline draft.');
  await actions.press(screen.getByRole('button', { name: 'Save note' }));
  expect(screen.getByText('Let’s check what was saved.')).toBeTruthy();
  expect(screen.getByLabelText('Note body').props.value).toContain(
    'Offline draft.',
  );
  expect(
    screen.getByRole('button', { name: 'Save note' }).props.accessibilityState
      .disabled,
  ).toBe(true);
  client.list.mockRejectedValueOnce(new ApiError('unavailable'));
  await actions.press(
    screen.getByRole('button', { name: 'Refresh saved notes' }),
  );
  expect(
    screen.getByRole('button', { name: 'Save note' }).props.accessibilityState
      .disabled,
  ).toBe(true);
  await actions.press(
    screen.getByRole('button', { name: 'Refresh saved notes' }),
  );
  expect(screen.getByText('Latest saved notes')).toBeTruthy();
  expect(client.save).toHaveBeenCalledTimes(1);
  expect(screen.getByLabelText('Note body').props.value).toContain(
    'Offline draft.',
  );
});

test('offline initial request recovers on refresh and dirty back preserves editing until confirmed', async () => {
  const client = mockClient();
  client.list.mockRejectedValueOnce(new ApiError('unavailable'));
  const actions = user();
  const alert = jest.spyOn(Alert, 'alert');
  await render(<Notebook client={client as unknown as NotesClient} />);
  await screen.findByText('A small interruption.');
  await actions.press(
    screen.getAllByRole('button', { name: 'Refresh notebook' })[0]!,
  );
  await screen.findByText(note.title);
  await actions.press(screen.getByRole('button', { name: '＋ Write a note' }));
  await enterText(screen.getByLabelText('Note title'), 'Keep me');
  await actions.press(screen.getByRole('button', { name: 'Back to notebook' }));
  expect(screen.getByLabelText('Note title').props.value).toBe('Keep me');
  await act(async () => {
    alert.mock.calls
      .at(-1)?.[2]
      ?.find((button) => button.text === 'Discard edits')
      ?.onPress?.();
  });
  await screen.findByText('YOUR COLLECTION');
});

test('pagination selects bounded server pages', async () => {
  const client = mockClient();
  client.list.mockResolvedValue({ ...page, total: 21 });
  const actions = user();
  await render(<Notebook client={client as unknown as NotesClient} />);
  await screen.findByText(note.title);
  await actions.press(screen.getByRole('button', { name: 'Next page' }));
  expect(client.list).toHaveBeenLastCalledWith(20);
});

test('missing records and unexpected failures show useful recovery without opening an editor', async () => {
  const client = mockClient();
  client.get.mockRejectedValueOnce(new Error('hidden failure'));
  const actions = user();
  await render(<Notebook client={client as unknown as NotesClient} />);
  await screen.findByText(note.title);
  await actions.press(
    screen.getByRole('button', { name: `Open note: ${note.title}` }),
  );
  expect(screen.getByText(/Something interrupted your notebook/)).toBeTruthy();
  expect(screen.queryByLabelText('Note body')).toBeNull();
  client.get.mockResolvedValueOnce({ id: 'one', title: note.title });
  await actions.press(
    screen.getByRole('button', { name: `Open note: ${note.title}` }),
  );
  expect(screen.getByLabelText('Note body').props.value).toBe('');
});
