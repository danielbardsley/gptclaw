export function normalize(message: string): string {
  const result = message.trim().replace(/\s+/g, " ");
  if (!result) throw new Error("Message must contain text");
  return result;
}
export function examples(offset: number, limit: number) {
  const all = [
    { id: 1, name: "First example" },
    { id: 2, name: "Second example" },
    { id: 3, name: "Third example" },
  ];
  return {
    items: all.slice(offset, offset + limit),
    total: all.length,
    offset,
    limit,
  };
}
