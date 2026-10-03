# Supaplex clone (x86 assembly, MASM)

A tile-based Supaplex-style game written in 32-bit MASM for the Assembly Language Programming course (TUCN, year III): player, walls, food, falling balls, circuits, explosions and a score. The level is loaded from `level.txt`, and sprites are drawn pixel by pixel from the `.inc` bitmap tables (source PNGs in `sprites/`).

`tapper (prototype)` is an earlier, much thinner game on the same framework.

Both build against the course's `canvas` drawing library (`canvas.lib` / `canvas.dll`), which is not included; the window loop and text routine at the top of each file come from its example program.
