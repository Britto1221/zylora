export const clientOverrides: Record<
  string,
  () => Promise<Record<string, unknown>>
> = {};

/*
Example paid override:

export const clientOverrides = {
  "bright-academy": () => import("./bright-academy"),
};
*/
