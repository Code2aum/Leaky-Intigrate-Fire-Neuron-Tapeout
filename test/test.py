# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge


async def tick(dut, n=1):
    """Wait n rising edges, then settle into ReadOnly phase so NBA updates are visible."""
    await ClockCycles(dut.clk, n)
    await ReadOnly()


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Clock period 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")   # fix: units → unit
    cocotb.start_soon(clock.start())

    # -------------------------------------------------------
    # Reset
    # -------------------------------------------------------
    dut._log.info("Reset")
    dut.ena.value   = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await tick(dut, 10)
    dut.rst_n.value = 1

    # -------------------------------------------------------
    # Test 1: Single cycle integration
    # state=0, current=20 → next = (0>>1)+20 = 20 → state=20
    # -------------------------------------------------------
    dut._log.info("Test 1: state=0, current=20 → state=20")
    dut.ui_in.value = 20
    await tick(dut, 1)
    assert int(dut.uo_out.value) == 20, f"T1: Expected 20, got {dut.uo_out.value}"
    assert int(dut.uio_out.value) == 0,  "T1: No spike expected"

    # -------------------------------------------------------
    # Test 2: Leak + integrate second cycle
    # state=20, current=20 → next = (20>>1)+20 = 10+20 = 30 → state=30
    # -------------------------------------------------------
    dut._log.info("Test 2: state=20, current=20 → state=30")
    await tick(dut, 1)
    assert int(dut.uo_out.value) == 30, f"T2: Expected 30, got {dut.uo_out.value}"

    # -------------------------------------------------------
    # Test 3: High current → spike fires within 10 cycles
    # -------------------------------------------------------
    dut._log.info("Test 3: High current, expect spike")
    dut.ui_in.value = 150
    spiked = False
    for i in range(10):
        await tick(dut, 1)
        spike_bit = (int(dut.uio_out.value) >> 7) & 1
        if spike_bit:
            dut._log.info(f"Spike fired at cycle {i+1}, state={dut.uo_out.value}")
            spiked = True
            break
    assert spiked, "T3: Expected spike with current=150 but none fired within 10 cycles"

    # -------------------------------------------------------
    # Test 4: After spike, membrane resets to 0
    # -------------------------------------------------------
    dut._log.info("Test 4: Post-spike membrane reset")
    dut.ui_in.value = 0
    await tick(dut, 1)
    assert int(dut.uo_out.value) == 0, f"T4: Expected state=0 after spike reset, got {dut.uo_out.value}"

    dut._log.info("All tests passed!")
