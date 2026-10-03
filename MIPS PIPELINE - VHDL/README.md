# MIPS pipeline (VHDL)

A 16-bit, five-stage pipelined MIPS processor for the Basys 3 board (Computer Architecture, TUCN, year II). The VHDL sources are in `src/`; `test_env.vhd` is the top level and holds the IF/ID, ID/EX, EX/MEM and MEM/WB pipeline registers. `docs/` has the report (Romanian) and the signal list. The `.xdc` is the Digilent Basys 3 master constraints file.
