# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # -------------------------------------------------------
    # Test 1: Single cycle integration
    # state=0 → next = (0>>1) + 20 = 20 → no spike → state=20
    # -------------------------------------------------------
    dut._log.info("Test 1: Integration (state=0, current=20 → state=20)")
    dut.ui_in.value = 20
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 20, f"Expected 20, got {dut.uo_out.value}"
    assert dut.uio_out.value == 0, "No spike expected"

    # -------------------------------------------------------
    # Test 2: Second cycle – leak and integrate again
    # state=20 → next = (20>>1) + 20 = 10 + 20 = 30 → state=30
    # -------------------------------------------------------
    dut._log.info("Test 2: Leak + Integration (state=20, current=20 → state=30)")
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 30, f"Expected 30, got {dut.uo_out.value}"

    # -------------------------------------------------------
    # Test 3: High current → spike + membrane reset
    # Apply large current (150) until spike fires (next >= 200)
    # -------------------------------------------------------
    dut._log.info("Test 3: High current spike test")
    dut.ui_in.value = 150
    spiked = False
    for _ in range(10):
        await ClockCycles(dut.clk, 1)
        spike_bit = int(dut.uio_out.value) >> 7  # bit 7 is the spike
        if spike_bit:
            dut._log.info(f"Spike fired! membrane was: {dut.uo_out.value}")
            spiked = True
            break
    assert spiked, "Expected a spike with current=150 but none fired within 10 cycles"

    # -------------------------------------------------------
    # Test 4: After spike, membrane should reset to 0
    # -------------------------------------------------------
    dut._log.info("Test 4: Post-spike reset check")
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0, f"Expected state=0 after spike reset, got {dut.uo_out.value}"

    dut._log.info("All tests passed!")
