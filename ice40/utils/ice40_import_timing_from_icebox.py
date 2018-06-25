#!/usr/bin/env python3
#
#  Copyright (C) 2018  Tim 'mithro' Ansell <me@mith.ro>
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
"""
Import the timing information from icebox into the following forms;

 * Stuff Verilog to Routing can use
 * [Standard Delay Format (SDF) format](https://en.wikipedia.org/wiki/Standard_Delay_Format) (for usage with .sim.v) models.



--



icestorm/icefuzz/timings_hx1k.html

"""


"""

# Standard Delay Format

Standard Delay Format (SDF) is an IEEE standard for the representation and
interpretation of timing data for use at any stage of an electronic design
process. It finds wide applicability in design flows, and forms an efficient
bridge between Dynamic timing verification and Static timing analysis

It has usually two sections: one for interconnect delays and the other for cell delays.

SDF format can be used for back-annotation as well as forward-annotation.



## Header

```
(DELAYFILE
    (SDFVERSION "2.1")
    (DESIGN "top")
    (VENDOR "verilog-to-routing")
    (PROGRAM "vpr")
    (VERSION "8.0.0-dev+vpr-7.0.5-6031-gc3f04a1d2-dirty")
    (DIVIDER /)
    (TIMESCALE 1 ps)
```

```
        //Writes out the SDF
        void print_sdf(int depth=0) {
            sdf_os_ << indent(depth) << "(DELAYFILE\n";
            sdf_os_ << indent(depth+1) << "(SDFVERSION \"2.1\")\n";
            sdf_os_ << indent(depth+1) << "(DESIGN \""<< top_module_name_ << "\")\n";
            sdf_os_ << indent(depth+1) << "(VENDOR \"verilog-to-routing\")\n";
            sdf_os_ << indent(depth+1) << "(PROGRAM \"vpr\")\n";
            sdf_os_ << indent(depth+1) << "(VERSION \"" << vtr::VERSION << "\")\n";
            sdf_os_ << indent(depth+1) << "(DIVIDER /)\n";
            sdf_os_ << indent(depth+1) << "(TIMESCALE 1 ps)\n";
            sdf_os_ << "\n";

            //Interconnect
            for(const auto& kv : logical_net_sinks_) {
                auto atom_net_id = kv.first;
                auto driver_iter = logical_net_drivers_.find(atom_net_id);
                VTR_ASSERT(driver_iter != logical_net_drivers_.end());
                auto driver_wire = driver_iter->second.first;
                auto driver_tnode = driver_iter->second.second;

                for(auto& sink_wire_tnode_pair : kv.second) {
                    auto sink_wire = sink_wire_tnode_pair.first;
                    auto sink_tnode = sink_wire_tnode_pair.second;

                    sdf_os_ << indent(depth+1) << "(CELL\n";
                    sdf_os_ << indent(depth+2) << "(CELLTYPE \"fpga_interconnect\")\n";
                    sdf_os_ << indent(depth+2) << "(INSTANCE " << escape_sdf_identifier(interconnect_name(driver_wire, sink_wire)) << ")\n";
                    sdf_os_ << indent(depth+2) << "(DELAY\n";
                    sdf_os_ << indent(depth+3) << "(ABSOLUTE\n";

                    double delay = get_delay_ps(driver_tnode, sink_tnode);

                    std::stringstream delay_triple;
                    delay_triple << "(" << delay << ":" << delay << ":" << delay << ")";

                    sdf_os_ << indent(depth+4) << "(IOPATH datain dataout " << delay_triple.str() << " " << delay_triple.str() << ")\n";
                    sdf_os_ << indent(depth+3) << ")\n";
                    sdf_os_ << indent(depth+2) << ")\n";
                    sdf_os_ << indent(depth+1) << ")\n";
                    sdf_os_ << indent(depth) << "\n";
                }
            }

            //Cells
            for(const auto& inst : cell_instances_) {
                inst->print_sdf(sdf_os_, depth+1);
            }

            sdf_os_ << indent(depth) << ")\n";
        }
```

## Escaping

//Escapes the given identifier to be safe for verilog
std::string escape_verilog_identifier(const std::string identifier) {
    //Verilog allows escaped identifiers
    //
    //The escaped identifiers start with a literal back-slash '\'
    //followed by the identifier and are terminated by white space
    //
    //We pre-pend the escape back-slash and append a space to avoid
    //the identifier gobbling up adjacent characters like commas which
    //are not actually part of the identifier
    std::string prefix = "\\";
    std::string suffix = " ";
    std::string escaped_name = prefix + identifier + suffix;

    return escaped_name;
}

//Returns true if c is categorized as a special character in SDF
bool is_special_sdf_char(char c) {
    //From section 3.2.5 of IEEE1497 Part 3 (i.e. the SDF spec)
    //Special characters run from:
    //    ! to # (ASCII decimal 33-35)
    //    % to / (ASCII decimal 37-47)
    //    : to @ (ASCII decimal 58-64)
    //    [ to ^ (ASCII decimal 91-94)
    //    ` to ` (ASCII decimal 96)
    //    { to ~ (ASCII decimal 123-126)
    //
    //Note that the spec defines _ (decimal code 95) and $ (decimal code 36)
    //as non-special alphanumeric characters.
    //
    //However it inconsistently also lists $ in the list of special characters.
    //Since the spec allows for non-special characters to be escaped (they are treated
    //normally), we treat $ as a special character to be safe.
    //
    //Note that the spec appears to have rendering errors in the PDF availble
    //on IEEE Xplore, listing the 'LEFT-POINTING DOUBLE ANGLE QUOTATION MARK'
    //character (decimal code 171) in place of the APOSTROPHE character '
    //with decimal code 39 in the special character list. We assume code 39.
    if((c >= 33 && c <= 35) ||
       (c == 36) || // $
       (c >= 37 && c <= 47) ||
       (c >= 58 && c <= 64) ||
       (c >= 91 && c <= 94) ||
       (c == 96) ||
       (c >= 123 && c <= 126)) {
        return true;
    }

    return false;
}

//Escapes the given identifier to be safe for sdf
std::string escape_sdf_identifier(const std::string identifier) {
    //SDF allows escaped characters
    //
    //We look at each character in the string and escape it if it is
    //a special character
    std::string escaped_name;

    for(char c : identifier) {
        if(is_special_sdf_char(c)) {
            //Escape the special character
            escaped_name += '\\';
        }
        escaped_name += c;
    }

    return escaped_name;
}

## Interconnect

 ???

```sdf
    (CELL
        (CELLTYPE "fpga_interconnect")
        (INSTANCE routing_segment_clk_output_0_0_to_SB_DFF_\$auto\$simplemap\.cc\:420\:simplemap_dff\$87_clock_0_0)
        (DELAY
            (ABSOLUTE
                (IOPATH datain dataout (1.35e+13:1.35e+13:1.35e+13) (1.35e+13:1.35e+13:1.35e+13))
            )
        )
    )
```



## LUT

```cpp
        void print_sdf(std::ostream& os, int depth) override {
            os << indent(depth) << "(CELL\n";
            os << indent(depth+1) << "(CELLTYPE \"" << type() << "\")\n";
            os << indent(depth+1) << "(INSTANCE " << escape_sdf_identifier(instance_name()) << ")\n";

            if(!timing_arcs().empty()) {
                os << indent(depth+1) << "(DELAY\n";
                os << indent(depth+2) << "(ABSOLUTE\n";

                for(auto& arc : timing_arcs()) {
                    double delay_ps = arc.delay();

                    std::stringstream delay_triple;
                    delay_triple << "(" << delay_ps << ":" << delay_ps << ":" << delay_ps << ")";

                    os << indent(depth+3) << "(IOPATH ";
                    //Note we do not escape the last index of multi-bit signals since they are used to
                    //match multi-bit ports
                    os << escape_sdf_identifier(arc.source_name()) << "[" << arc.source_ipin() << "]" << " ";

                    VTR_ASSERT(arc.sink_ipin() == 0); //Should only be one output
                    os << escape_sdf_identifier(arc.sink_name()) << " ";
                    os << delay_triple.str() << " " << delay_triple.str() << ")\n";
                }
                os << indent(depth+2) << ")\n";
                os << indent(depth+1) << ")\n";
            }

            os << indent(depth) << ")\n";
            os << indent(depth) << "\n";
        }
```

```sdf
    (CELL
        (CELLTYPE "LUT_K")
        (INSTANCE lut_\$abc\$1289\$n57_1)
        (DELAY
            (ABSOLUTE
                (IOPATH in[0] out (10:10:10) (10:10:10))
                (IOPATH in[1] out (10:10:10) (10:10:10))
                (IOPATH in[2] out (10:10:10) (10:10:10))
                (IOPATH in[3] out (10:10:10) (10:10:10))
            )
        )
    )
```


## Latch

```cpp
        void print_sdf(std::ostream& os, int depth=0) override {
            VTR_ASSERT(type_ == Type::RISING_EDGE);

            os << indent(depth) << "(CELL\n";
            os << indent(depth+1) << "(CELLTYPE \"" << "DFF" << "\")\n";
            os << indent(depth+1) << "(INSTANCE " << escape_sdf_identifier(instance_name_) << ")\n";

            //Clock to Q
            if(!std::isnan(tcq_)) {
                os << indent(depth+1) << "(DELAY\n";
                os << indent(depth+2) << "(ABSOLUTE\n";
                    double delay_ps = get_delay_ps(tcq_);

                    std::stringstream delay_triple;
                    delay_triple << "(" << delay_ps << ":" << delay_ps << ":" << delay_ps << ")";

                    os << indent(depth+3) << "(IOPATH " << "(posedge clock) Q " << delay_triple.str() << " " << delay_triple.str() << ")\n";
                os << indent(depth+2) << ")\n";
                os << indent(depth+1) << ")\n";
            }

            //Setup/Hold
            if(!std::isnan(tsu_) || !std::isnan(thld_)) {
                os << indent(depth+1) << "(TIMINGCHECK\n";
                if(!std::isnan(tsu_)) {
                    std::stringstream setup_triple;
                    double setup_ps = get_delay_ps(tsu_);
                    setup_triple << "(" << setup_ps << ":" << setup_ps << ":" << setup_ps << ")";
                    os << indent(depth+2) << "(SETUP D (posedge clock) " << setup_triple.str() << ")\n";
                }
                if(!std::isnan(thld_)) {
                    std::stringstream hold_triple;
                    double hold_ps = get_delay_ps(thld_);
                    hold_triple << "(" << hold_ps << ":" << hold_ps << ":" << hold_ps << ")";
                    os << indent(depth+2) << "(HOLD D (posedge clock) " << hold_triple.str() << ")\n";
                }
            }
            os << indent(depth+1) << ")\n";
            os << indent(depth) << ")\n";
            os << indent(depth) << "\n";
        }
```

## Blackbox

```cpp
        void print_sdf(std::ostream& os, int depth=0) override {
            os << indent(depth) << "(CELL\n";
            os << indent(depth+1) << "(CELLTYPE \"" << type_name_ << "\")\n";
            os << indent(depth+1) << "(INSTANCE " << escape_sdf_identifier(inst_name_) << ")\n";
            os << indent(depth+1) << "(DELAY\n";

            if(!timing_arcs_.empty() || !ports_tcq_.empty()) {
                os << indent(depth+2) << "(ABSOLUTE\n";

                //Combinational paths
                for(const auto& arc : timing_arcs_) {
                    double delay_ps = get_delay_ps(arc.delay());

                    std::stringstream delay_triple;
                    delay_triple << "(" << delay_ps << ":" << delay_ps << ":" << delay_ps << ")";

                    //Note that we explicitly do not escape the last array indexing so an SDF
                    //reader will treat the ports as multi-bit
                    //
                    //We also only put the last index in if the port has multiple bits
                    os << indent(depth+3) << "(IOPATH ";
                    os << escape_sdf_identifier(arc.source_name());
                    if(find_port_size(arc.source_name()) > 1) {
                        os << "[" << arc.source_ipin() << "]";
                    }
                    os << " ";
                    os << escape_sdf_identifier(arc.sink_name());
                    if(find_port_size(arc.sink_name()) > 1) {
                        os << "[" << arc.sink_ipin() << "]";
                    }
                    os << " ";
                    os << delay_triple.str();
                    os << ")\n";
                }

                //Clock-to-Q delays
                for(auto kv : ports_tcq_) {
                    double clock_to_q_ps = get_delay_ps(kv.second);

                    std::stringstream delay_triple;
                    delay_triple << "(" << clock_to_q_ps << ":" << clock_to_q_ps << ":" << clock_to_q_ps << ")";

                    os << indent(depth+3) << "(IOPATH (posedge clock) " << escape_sdf_identifier(kv.first) << " " << delay_triple.str() << " " << delay_triple.str() << ")\n";
                }
                os << indent(depth+2) << ")\n"; //ABSOLUTE
            }
            os << indent(depth+1) << ")\n"; //DELAY

            if(!ports_tsu_.empty() || !ports_thld_.empty()) {
                //Setup checks
                os << indent(depth+1) << "(TIMINGCHECK\n";
                for(auto kv : ports_tsu_) {
                    double setup_ps = get_delay_ps(kv.second);

                    std::stringstream delay_triple;
                    delay_triple << "(" << setup_ps << ":" << setup_ps << ":" << setup_ps << ")";

                    os << indent(depth+2) << "(SETUP " << escape_sdf_identifier(kv.first) << " (posedge clock) " << delay_triple.str() << ")\n";
                }
                for(auto kv : ports_thld_) {
                    double hold_ps = get_delay_ps(kv.second);

                    std::stringstream delay_triple;
                    delay_triple << "(" << hold_ps << ":" << hold_ps << ":" << hold_ps << ")";

                    os << indent(depth+2) << "(HOLD " << escape_sdf_identifier(kv.first) << " (posedge clock) " << delay_triple.str() << ")\n";
                }
                os << indent(depth+1) << ")\n"; //TIMINGCHECK
            }
            os << indent(depth) << ")\n"; //CELL
        }
```

```sdf
    (CELL
        (CELLTYPE "SB_DFF")
        (INSTANCE SB_DFF_\$auto\$simplemap\.cc\:420\:simplemap_dff\$87)
        (DELAY
        )
    )
```

"""







"""
Verilog to Routing Timing models

The best documentation to understand Verilog to Routing Timing models is the
[Primitive Block Timing Modeling Tutorial](https://docs.verilogtorouting.org/en/latest/tutorials/arch/timing_modeling/#arch-model-timing-tutorial).

There is also useful information in the
[Post-Implementation Timing Simulation](https://docs.verilogtorouting.org/en/latest/tutorials/timing_simulation/)
section of the docs.


## [Combinational Block](https://docs.verilogtorouting.org/en/latest/tutorials/arch/timing_modeling/#arch-model-timing-tutorial)

```
<model name="adder">
  <input_ports>
    <port name="a" combinational_sink_ports="sum cout"/>
    <port name="b" combinational_sink_ports="sum cout"/>
    <port name="cin" combinational_sink_ports="sum cout"/>
  </input_ports>
  <output_ports>
    <port name="sum"/>
    <port name="cout"/>
  </output_ports>
</model>

<pb_type name="adder" blif_model=".subckt adder" num_pb="1">
  <input name="a" num_pins="1"/>
  <input name="b" num_pins="1"/>
  <input name="cin" num_pins="1"/>
  <output name="cout" num_pins="1"/>
  <output name="sum" num_pins="1"/>

  <delay_constant max="300e-12" in_port="adder.a" out_port="adder.sum"/>
  <delay_constant max="300e-12" in_port="adder.b" out_port="adder.sum"/>
  <delay_constant max="300e-12" in_port="adder.cin" out_port="adder.sum"/>
  <delay_constant max="300e-12" in_port="adder.a" out_port="adder.cout"/>
  <delay_constant max="300e-12" in_port="adder.b" out_port="adder.cout"/>
  <delay_constant max="10e-12" in_port="adder.cin" out_port="adder.cout"/>
</pb_type>
```

## [Sequential block (no internal paths)](https://docs.verilogtorouting.org/en/latest/tutorials/arch/timing_modeling/#sequential-block-no-internal-paths)

```
<model name="dff">
  <input_ports>
    <port name="d" clock="clk"/>
    <port name="clk" is_clock="1"/>
  </input_ports>
  <output_ports>
    <port name="q" clock="clk/>
  </output_ports>
</model>

<pb_type name="ff" blif_model=".subckt dff" num_pb="1">
  <input name="D" num_pins="1"/>
  <output name="Q" num_pins="1"/>
  <clock name="clk" num_pins="1"/>

  <T_setup value="66e-12" port="ff.D" clock="clk"/>
  <T_clock_to_Q max="124e-12" port="ff.Q" clock="clk"/>
</pb_type>
```

# Interconnect Timing

## Nodes

```<timing R="float" C="float">```

This optional subtag contains information used for timing analysis

Required Attributes:
 * R - The resistance that goes through this node. This is only the metal
       resistance, it does not include the resistance of the switch that leads
       to another routing resource node.

 * C - The total capacitance of this node. This includes the metal capacitance,
       input capacitance of all the switches hanging off the node, the output
       capacitance of all the switches to the node, and the connection box
       buffer capacitances that hangs off it.

## Switches


```<timing R="float" cin="float" Cout="float" Tdel="float/>```

This optional subtag contains information used for timing analysis. Without it,
the program assums all subtags to contain a value of 0.

Optional Attributes:
 * R, Cin, Cout – The resistance, input capacitance and output capacitance of the switch.
 * Tdel – Switch’s intrinsic delay. It can be outlined that the delay through an unloaded switch is Tdel + R * Cout.

```<sizing mux_trans_size="int" buf_size="float"/>```

The sizing information contains all the information needed for area calculation.
Required Attributes:
 * mux_trans_size – The area of each transistor in the segment’s driving mux. This is measured in minimum width transistor units.
 * buf_size – The area of the buffer. If this is set to zero, the area is calculated from the resistance.

## Segments

```<timing R_per_meter="float" C_per_meter="float">```
This optional tag defines the timing information of this segment.

Optional Attributes:
 * R_per_meter, C_per_meter – The resistance and capacitance of a routing track, per unit logic block length.



```
<delay_constant max="float" min="float" in_port="string" out_port="string"/>
```


Describe a timing matrix for all edges going from in_port to out_port.

 * Number of rows of matrix should equal the number of inputs,
 * Number of columns should equal the number of outputs.

To specify both max and min delays two <delay_matrix> should be used.

Example: The following defines a delay matrix for a 4-bit input port in, and
3-bit output port out:
```xml
<delay_matrix type="max" in_port="in" out_port="out">
    1.2e-10 1.4e-10 3.2e-10
    4.6e-10 1.9e-10 2.2e-10
    4.5e-10 6.7e-10 3.5e-10
    7.1e-10 2.9e-10 8.7e-10
</delay>
```

```
<T_setup value="float" port="string" clock="string"/>
<T_hold value="float" port="string" clock="string"/>
<T_clock_to_Q max="float" min="float" port="string" clock="string"/>
```

```
<pb_type name="seq_foo" blif_model=".subckt seq_foo" num_pb="1">
    <input name="in" num_pins="4"/>
    <output name="out" num_pins="1"/>
    <clock name="clk" num_pins="1"/>

    <!-- external -->
    <T_setup value="80e-12" port="seq_foo.in" clock="clk"/>
    <T_clock_to_Q max="20e-12" port="seq_foo.out" clock="clk"/>

    <!-- internal -->
    <T_clock_to_Q max="10e-12" port="seq_foo.in" clock="clk"/>
    <delay_constant max="0.9e-9" in_port="seq_foo.in" out_port="seq_foo.out"/>
    <T_setup value="90e-12" port="seq_foo.out" clock="clk"/>
</pb_type>
```

```
<model name="simple_pll">
  <input_ports>
    <port name="in_clock" is_clock="1"/>
  <input_ports/>
  <output_ports>
    <port name="out_clock" is_clock="1"/>
  <output_ports/>
</model>
```



<clock C_wire="float" C_wire_per_m="float" buffer_size={"float"|"auto"}/>
Optional Attributes:
 * C_wire – The absolute capacitance, in Farads, of the wire between each clock buffer.
 * C_wire_per_m – The wire capacitance, in Farads per Meter.
 * buffer_size – The size of each clock buffer.

"""



# Python libs
import logging
import operator
import os.path
import re
import sys
from collections import namedtuple, OrderedDict
from functools import reduce
from os.path import commonprefix

MYDIR = os.path.dirname(__file__)

# Third party libs
import lxml.etree as ET

sys.path.insert(0, os.path.join(MYDIR, "..", "..", "third_party", "icestorm", "icebox"))
import icebox
import icebox_asc2hlc

# Local libs
sys.path.insert(0, os.path.join(MYDIR, "..", "..", "utils"))
import lib.rr_graph.graph as graph
import lib.rr_graph.channel as channel
from lib.rr_graph import Offset
from lib.asserts import assert_type

ic = None


class PositionIcebox(graph.Position):
    def __str__(self):
        return "PI(%2s,%2s)" % self
    def __repr__(self):
        return str(self)


class PositionVPR(graph.Position):
    def __str__(self):
        return "PV(%2s,%2s)" % self
    def __repr__(self):
        return str(self)


def pos_icebox2vpr(pos):
    '''Convert icebox to VTR coordinate system by adding 1 for dummy blocks'''
    assert_type(pos, PositionIcebox)
    return PositionVPR(pos.x + 2, pos.y + 2)


def pos_vpr2icebox(pos):
    '''Convert VTR to icebox coordinate system by subtracting 1 for dummy blocks'''
    assert_type(pos, PositionVPR)
    return PositionIcebox(pos.x - 2, pos.y - 2)


def pos_icebox2vprpin(pos):
    if pos.x == 0:
        return PositionVPR(1, pos.y+2)
    elif pos.y == 0:
        return PositionVPR(pos.x+2, 1)
    elif pos.x == ic.max_x:
        return PositionVPR(pos.x+2+1, pos.y+2)
    elif pos.y == ic.max_y:
        return PositionVPR(pos.x+2, pos.y+2+1)
    assert False, (pos, (ic.max_x, ic.max_y))


class RunOnStr:
    """Don't run function until a str() is called."""
    def __init__(self, f, *args, **kw):
        self.f = f
        self.args = args
        self.kw = kw
        self.s = None

    def __str__(self):
        if not self.s:
            self.s = self.f(*self.args, **self.kw)
        return self.s


def format_node(g, node):
    if node is None:
        return "None"
    assert isinstance(node, ET._Element), node
    if node.tag == "node":
        return RunOnStr(graph.RoutingGraphPrinter.node, node, g.block_grid)
    elif node.tag == "edge":
        return RunOnStr(graph.RoutingGraphPrinter.edge, g.routing, node, g.block_grid)


def format_entry(e):
    try:
        bits, sw, src, dst, *args = e
    except ValueError:
        return str(e)
    if args:
        args = " " + str(args)
    else:
        args = ""
    return RunOnStr(operator.mod, "[%s %s %s %s%s]", (",".join(bits), sw, src, dst, args))


def is_corner(ic, pos):
    return pos in (
        (0, 0), (0, ic.max_y), (ic.max_x, 0), (ic.max_x, ic.max_y))


def tiles(ic):
    for x in range(ic.max_x + 1):
        for y in range(ic.max_y + 1):
            p = PositionIcebox(x, y)
            if is_corner(ic, p):
                continue
            yield p


def find_path(group):
    assert_type(group, list)
    start = group[0][0]
    end = group[0][0]
    for ipos, netname in group:
        assert_type(ipos, PositionIcebox)
        if ipos < start:
            start = ipos
        if ipos > end:
            end = ipos
    return start, end


def filter_track_names(group):
    assert_type(group, list)
    names = []
    for ipos, netname in group:
        assert_type(ipos, PositionIcebox)
        # FIXME: Get the neighbourhood wires working.
        if "neigh_op" in netname:
            continue
        # FIXME: Get the logic_op wires working.
        if "logic_op" in netname:
            continue
        # FIXME: Get the sp4_r_v_ wires working
        if "sp4_r_v_" in netname:
            continue
        # FIXME: Fix the carry logic.
        if "cout" in netname or "carry_in" in netname:
            continue
        if "lout" in netname:
            continue
        names.append((ipos, netname))
    return names


def filter_non_straight(group):
    assert_type(group, list)
    x_count = {}
    y_count = {}
    for ipos, netname in group:
        assert_type(ipos, PositionIcebox)
        if ipos.x not in x_count:
            x_count[ipos.x] = 0
        x_count[ipos.x] += 1
        if ipos.y not in y_count:
            y_count[ipos.y] = 0
        y_count[ipos.y] += 1
    x_val = list(sorted((c, x) for x, c in x_count.items()))
    y_val = list(sorted((c, y) for y, c in y_count.items()))

    good = []
    skipped = []
    if x_val[-1][0] > y_val[-1][0]:
        x_ipos = x_val[-1][1]
        for ipos, netname in group:
            if ipos.x != x_ipos:
                skipped.append((ipos, netname))
                continue
            good.append((ipos, netname))
    else:
        y_ipos = y_val[-1][1]
        for ipos, netname in group:
            if ipos.y != y_ipos:
                skipped.append((ipos, netname))
                continue
            good.append((ipos, netname))
    return good, skipped


def group_hlc_name(group):
    assert_type(group, list)
    global ic
    hlcnames = set()
    for ipos, localname in group:
        assert_type(ipos, PositionIcebox)
        hlcname = icebox_asc2hlc.translate_netname(*ipos, ic.max_x-1, ic.max_y-1, localname)
        hlcnames.add(hlcname)
    assert len(hlcnames) == 1, hlcnames
    return hlcnames.pop()


def group_seg_type(group):
    assert_type(group, list)
    for ipos, netname in group:
        assert_type(ipos, PositionIcebox)
        if "local" in netname:
            return "local"
        if "global" in netname:
            return "global"
        if "sp4" in netname or "span4" in netname:
            return "span4"
        if "sp12" in netname or "span12" in netname:
            return "span12"
    return "unknown"


def group_chan_type(group):
    assert_type(group, list)
    for ipos, netname in group:
        assert_type(ipos, PositionIcebox)
        if "local" in netname:
            return channel.Track.Type.Y
        if "_h" in netname:
            return channel.Track.Type.X
        if "_v" in netname:
            return channel.Track.Type.Y
    return None


def init(device_name, read_rr_graph):
    global ic
    ic = icebox.iceconfig()
    {
        #'t4':  ic.setup_empty_t4,
        '8k': ic.setup_empty_8k,
        '5k': ic.setup_empty_5k,
        '1k': ic.setup_empty_1k,
        '384': ic.setup_empty_384,
    }[device_name]()

    print('Loading rr_graph')
    g = graph.Graph(read_rr_graph, clear_fabric=True)
    g.set_tooling(
        name="icebox",
        version="dev",
        comment="Generated for iCE40 {} device".format(device_name))

    return ic, g


def add_pin_aliases(g, ic):
    '''Build a list of icebox global pin names to Graph node IDs'''
    name_rr2local = {}

    # FIXME: quick attempt, not thoroughly checked
    # BLK_TL-PLB
    # http://www.clifford.at/icestorm/logic_tile.html
    # http://www.clifford.at/icestorm/bitdocs-1k/tile_1_1.html
    name_rr2local['BLK_TL-PLB.lutff_global/s_r[0]'] = 'lutff_global/s_r'
    name_rr2local['BLK_TL-PLB.lutff_global/clk[0]'] = 'lutff_global/clk'
    name_rr2local['BLK_TL-PLB.lutff_global/cen[0]'] = 'lutff_global/cen'
    # FIXME: these two are wrong I think, but don't worry about carry for now
    #name_rr2local['BLK_TL-PLB.FCIN[0]'] = 'lutff_0/cin'
    #name_rr2local['BLK_TL-PLB.FCOUT[0]'] = 'lutff_7/cout'
    #name_rr2local['BLK_TL-PLB.lutff_0_cin[0]'] = 'lutff_0/cin'
    #name_rr2local['BLK_TL-PLB.lutff_7_cout[0]'] = 'lutff_7/cout'
    for luti in range(8):
        name_rr2local['BLK_TL-PLB.lutff_{}/out[0]'.format(
            luti)] = 'lutff_{}/out'.format(luti)
        for lut_input in range(4):
            name_rr2local['BLK_TL-PLB.lutff_{}/in[{}]'.format(
                luti, lut_input)] = 'lutff_{}/in_{}'.format(
                    luti, lut_input)

    name_rr2local['BLK_TL-PLB.FCOUT[0]'] = 'lutff_0/cout'

    # BLK_TL-PIO
    # http://www.clifford.at/icestorm/io_tile.html
    # FIXME: filter out orientations that don't exist?
    for blocki in range(2):
        name_rr2local['BLK_TL-PIO.[{}]LATCH[0]'.format(
            blocki)] = 'io_{}/latch'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]OUTCLK[0]'.format(
            blocki)] = 'io_{}/outclk'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]CEN[0]'.format(
            blocki)] = 'io_{}/cen'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]INCLK[0]'.format(
            blocki)] = 'io_{}/inclk'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]D_IN_0[0]'.format(
            blocki)] = 'io_{}/D_IN_0'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]D_IN_1[0]'.format(
            blocki)] = 'io_{}/D_IN_1'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]D_OUT_0[0]'.format(
            blocki)] = 'io_{}/D_OUT_0'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]D_OUT_1[0]'.format(
            blocki)] = 'io_{}/D_OUT_1'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]OUT_ENB[0]'.format(
            blocki)] = 'io_{}/OUT_ENB'.format(blocki)
        name_rr2local['BLK_TL-PIO.[{}]PACKAGE_PIN[0]'.format(
            blocki)] = 'io_{}/pin'.format(blocki)

    # BLK_TL-RAM
    for top_bottom in 'BT':
        # rdata, wdata, and mask ranges are the same based on Top/Bottom
        if top_bottom == 'T':
            data_range = range(8,16)
            # top has Read clock and enbable and address
            rw = 'R'
        else:
            data_range = range(0,8)
            # top has Read clock and enbable and address
            rw = 'W'

        def add_ram_pin(rw, sig, ind=None):
            if ind is None:
                name_rr2local['BLK_TL-RAM.{}{}[{}]'.format(rw, sig, 0)] = 'ram/{}{}'.format(rw, sig)
            else:
                name_rr2local['BLK_TL-RAM.{}{}[{}]'.format(rw, sig, ind)] = 'ram/{}{}_{}'.format(rw, sig, ind)

        add_ram_pin(rw, 'CLK')
        add_ram_pin(rw, 'CLKE')
        add_ram_pin(rw, 'E')

        for ind in range(11):
            add_ram_pin(rw, 'ADDR', ind)

        for ind in data_range:
            add_ram_pin('R', 'DATA', ind)
            add_ram_pin('W', 'DATA', ind)
            add_ram_pin('', 'MASK', ind)

    for block in g.block_grid:
        for pin in block.pins:
            if "RAM" in block.block_type.name:
                pin_pos = block.position + ram_pin_offset(pin)
            else:
                pin_pos = block.position
            vpos = PositionVPR(*pin_pos)
            ipos = pos_vpr2icebox(vpos)

            node = g.routing.localnames[(pin_pos, pin.name)]
            node.set_metadata("hlc_coord", "{},{}".format(*ipos))

            logging.debug("On %s for %s", vpos, format_node(g, node))

            hlc_name = name_rr2local.get(
                pin.xmlname, group_hlc_name([(ipos, pin.name)]))
            logging.debug(
                " Setting local name %s on %s for %s",
                hlc_name, vpos, format_node(g, node))
            g.routing.localnames.add(vpos, hlc_name, node)
            node.set_metadata("hlc_name", hlc_name)

            rr_name = pin.xmlname
            try:
                localname = name_rr2local[rr_name]
            except KeyError:
                logging.warn(
                    "On %s rr_name %s doesn't have a translation",
                    ipos, rr_name)
                continue

            # FIXME: only add for actual position instead for all
            if localname == hlc_name:
                logging.debug(
                    " Local name %s same as hlc_name on %s for %s",
                    localname, vpos, format_node(g, node))
            else:
                assert False, "{} != {}".format(localname, hlc_name)
                logging.debug(
                    " Setting local name %s on %s for %s",
                    localname, vpos, format_node(g, node))
                g.routing.localnames.add(vpos, localname, node)


def add_dummy_tracks(g, ic):
    """Add a single dummy track to every channel."""
    dummy = g.segments["dummy"]
    for x in range(-2, ic.max_x+2):
        istart = PositionIcebox(x, 0)
        iend = PositionIcebox(x, ic.max_y)
        track, track_node = g.create_xy_track(
            pos_icebox2vpr(istart), pos_icebox2vpr(iend),
            segment=dummy,
            direction=channel.Track.Direction.BI)
    for y in range(-2, ic.max_y+2):
        istart = PositionIcebox(0, y)
        iend = PositionIcebox(ic.max_x, y)
        track, track_node = g.create_xy_track(
            pos_icebox2vpr(istart), pos_icebox2vpr(iend),
            segment=dummy,
            direction=channel.Track.Direction.BI)


def add_global_tracks(g, ic):
    """Add the global tracks to every channel."""
    def skip(fmt, *args, **kw):
        raise AssertionError(fmt % args)

    GLOBAL_SPINE_ROW = ic.max_x // 2
    GLOBAL_BUF = "GLOBAL_BUFFER_OUTPUT"
    padin_db = ic.padin_pio_db()
    iolatch_db = ic.iolatch_db()

    # Create the 8 global networks
    glb = g.segments["global"]
    short = g.switches["__vpr_delayless_switch__"]
    for i in range(0, 8):
        glb_name = "glb_netwk_{}".format(i)

        # Vertical global wires
        for x in range(0, ic.max_x+1):
            istart = PositionIcebox(x, 0)
            iend = PositionIcebox(x, ic.max_y)
            track, track_node = g.create_xy_track(
                pos_icebox2vpr(istart), pos_icebox2vpr(iend),
                segment=glb,
                typeh=channel.Track.Type.Y,
                direction=channel.Track.Direction.BI)
            track_node.set_metadata("hlc_name", glb_name)
            for y in range(0, ic.max_y+1):
                ipos = PositionIcebox(x, y)
                vpos = pos_icebox2vpr(ipos)
                g.routing.localnames.add(vpos, glb_name, track_node)

        # One horizontal wire
        istart = PositionIcebox(0, GLOBAL_SPINE_ROW)
        iend = PositionIcebox(ic.max_x+1, GLOBAL_SPINE_ROW)
        track, track_node = g.create_xy_track(
            pos_icebox2vpr(istart), pos_icebox2vpr(iend),
            segment=glb,
            typeh=channel.Track.Type.X,
            direction=channel.Track.Direction.BI)
        track_node.set_metadata("hlc_name", glb_name)

        for x in range(0, ic.max_x+1):
            ipos = PositionIcebox(x, GLOBAL_SPINE_ROW)
            vpos = pos_icebox2vpr(ipos)
            g.routing.localnames.add(vpos, glb_name+"_h", track_node)

        # Connect the vertical wires to the horizontal one to make a single
        # global network
        for x in range(0, ic.max_x+1):
            ipos = PositionIcebox(x, GLOBAL_SPINE_ROW)
            create_edge_with_names(
                g,
                glb_name, glb_name+"_h",
                ipos, short,
                skip,
                bidir=True,
            )

    # Create the padin_X localname aliases for the glb_network_Y
    # FIXME: Why do these exist!?
    for n, (gx, gy, gz) in enumerate(padin_db):
        vpos = pos_icebox2vpr(PositionIcebox(gx, gy))

        glb_name = "glb_netwk_{}".format(n)
        glb_node = g.routing.get_by_name(glb_name, vpos)
        g.routing.localnames.add(vpos, "padin_{}".format(gz), glb_node)

    # Create the IO->global drivers which exist in some IO tiles.
    for n, (gx, gy, gz) in enumerate(padin_db):
        ipos = PositionIcebox(gx, gy)
        vpos = pos_icebox2vpr(ipos)

        # Create the GLOBAL_BUFFER_OUTPUT track and short it to the
        # PACKAGE_PIN output of the correct IO subtile.
        track, track_node = g.create_xy_track(
            vpos, vpos,
            segment=glb,
            typeh=channel.Track.Type.Y,
            direction=channel.Track.Direction.BI)
        track_node.set_metadata(
            "hlc_name", "io_{}/{}".format(gz, GLOBAL_BUF))
        g.routing.localnames.add(vpos, GLOBAL_BUF, track_node)

        create_edge_with_names(
            g,
            "io_{}/pin".format(gz), GLOBAL_BUF,
            ipos, short,
            skip,
        )

        # Create the switch to enable the GLOBAL_BUFFER_OUTPUT track to
        # drive the global network.
        create_edge_with_names(
            g,
            GLOBAL_BUF, "glb_netwk_{}".format(n),
            ipos, g.switches["buffer"],
            skip,
        )

    # Work out for which tiles the fabout is directly shorted to a global
    # network.
    fabout_to_glb = {}
    for gn, (gx, gy, gz) in enumerate(padin_db):
        ipos = PositionIcebox(gx, gy)
        assert ipos not in fabout_to_glb, (ipos, fabout_to_glb)
        gn = None
        for igx, igy, ign in ic.gbufin_db():
            if ipos == (igx, igy):
                gn = ign
        assert gn is not None, (ipos, gz, gn)

        fabout_to_glb[ipos] = (gz, gn)

    # Create the nets which are "global" to an IO tile pair.
    for ipos in list(tiles(ic)):
        tile_type = ic.tile_type(*ipos)
        if tile_type != "IO":
            continue

        vpos = pos_icebox2vpr(ipos)

        # Create the "io_global" signals inside a tile
        io_names = [
            "inclk",
            "outclk",
            "cen",
            "latch",
        ]
        for name in io_names:
            glb_name = "io_global/{}".format(name)

            hlc_name = group_hlc_name([(ipos, glb_name)])
            track, track_node = g.create_xy_track(
                vpos, vpos,
                segment=glb,
                typeh=channel.Track.Type.Y,
                direction=channel.Track.Direction.BI)
            track_node.set_metadata("hlc_name", hlc_name)
            g.routing.localnames.add(vpos, glb_name, track_node)

            # Connect together the io_global signals inside a tile
            for i in range(2):
                local_name = "io_{}/{}".format(i, name)
                create_edge_with_names(
                    g,
                    glb_name,
                    local_name,
                    ipos, short,
                    skip,
                )

        # Create the fabout track. Every IO tile has a fabout track, but
        # sometimes the track is special;
        # - drives a glb_netwk_X,
        # - drives the io_global/latch for the bank
        hlc_name = group_hlc_name([(ipos, "fabout")])
        track, track_node = g.create_xy_track(
            vpos, vpos,
            segment=glb,
            typeh=channel.Track.Type.Y,
            direction=channel.Track.Direction.BI)
        track_node.set_metadata("hlc_name", hlc_name)
        g.routing.localnames.add(vpos, "fabout", track_node)

        # Fabout drives a global network?
        if ipos in fabout_to_glb:
            gz, gn = fabout_to_glb[ipos]
            create_edge_with_names(
                g,
                "fabout", "glb_netwk_{}".format(gn),
                ipos, short,
                skip,
            )

        # Fabout drives the io_global/latch?
        if ipos in iolatch_db:
            create_edge_with_names(
                g,
                "fabout", "io_global/latch",
                ipos, short,
                skip,
            )


def create_edge_with_names(g, src_name, dst_name, ipos, switch, skip, bidir=False):
    src_hlc_name = group_hlc_name([(ipos, src_name)])
    dst_hlc_name = group_hlc_name([(ipos, dst_name)])

    vpos = pos_icebox2vpr(ipos)
    src_node = g.routing.get_by_name(src_name, vpos, None)
    dst_node = g.routing.get_by_name(dst_name, vpos, None)

    if src_node is None:
        skip(
            "src missing *%s:%s* (%s) node %s => %s:%s (%s) node %s",
            vpos,
            src_name,
            src_hlc_name,
            format_node(g, src_node),
            vpos,
            dst_name,
            dst_hlc_name,
            format_node(g, dst_node),
            level=logging.WARNING,
        )
        return
    if dst_node is None:
        skip(
            "dst missing %s:%s (%s) node %s => *%s:%s* (%s) node %s",
            vpos,
            src_name,
            src_hlc_name,
            format_node(g, src_node),
            vpos,
            dst_name,
            dst_hlc_name,
            format_node(g, dst_node),
        )
        return

    logging.debug(
        "On %s add %-8s edge %s - %s:%s (%s) node %s => %s:%s (%s) node %s",
        ipos,
        switch.name,
        len(g.routing.id2element[graph.RoutingEdge]),
        vpos,
        src_name,
        src_hlc_name,
        format_node(g, src_node),
        vpos,
        dst_name,
        dst_hlc_name,
        format_node(g, dst_node),
    )

    edge = g.routing.create_edge_with_nodes(src_node, dst_node, switch=switch)
    edge.set_metadata("hlc_coord", "{},{}".format(*ipos))
    if bidir:
        edge = g.routing.create_edge_with_nodes(dst_node, src_node, switch=switch)
        edge.set_metadata("hlc_coord", "{},{}".format(*ipos))


def add_tracks(g, ic, all_group_segments, segtype_filter=None):
    add_dummy_tracks(g, ic)

    for group in sorted(all_group_segments):
        group = [(PositionIcebox(x, y), netname) for x, y, netname in group]

        segtype = group_seg_type(group)
        if segtype_filter is not None and segtype != segtype_filter:
            continue
        if segtype == "unknown":
            logging.debug("Skipping unknown track group: %s", group)
            continue
        if segtype == "global":
            logging.debug("Skipping global track group: %s", group)
            continue
        segment = g.segments[segtype]

        fgroup = filter_track_names(group)
        if not fgroup:
            logging.debug("Filtered out track group: %s", group)
            continue

        fgroup, skipped = filter_non_straight(fgroup)
        assert len(fgroup) > 0, (fgroup, fgroup)
        if len(skipped) > 0:
            logging.debug("""Filtered non-straight segments;
 Skipping: %s
Remaining: %s""", skipped, fgroup)

        hlc_name = group_hlc_name(group)

        istart, iend = find_path(fgroup)
        if istart.x == iend.x and istart.y != iend.y:
            typeh = channel.Track.Type.Y
        elif istart.x != iend.x and istart.y == iend.y:
            typeh = channel.Track.Type.X
        elif istart.x != iend.x and istart.y != iend.y:
            logging.warn("Skipping non-straight track group: %s (%s)", fgroup, group)
            continue
        else:
            typeh = group_chan_type(fgroup)
        vstart, vend = pos_icebox2vpr(istart), pos_icebox2vpr(iend)

        track, track_node = g.create_xy_track(
            vstart, vend,
            segment=segment,
            typeh=typeh,
            direction=channel.Track.Direction.BI)

        track_fmt = format_node(g, track_node)
        logging.debug(
            "Created track %s %s %s from %s %s",
            hlc_name, track_fmt, segment.name, typeh, group)

        track_node.set_metadata("hlc_name", hlc_name)
        if segtype != "local":
            g.routing.globalnames.add(hlc_name, track_node)
            logging.debug(
                " Setting global name %s for %s",
                hlc_name, track_fmt)

        for pos, netname in fgroup:
            vpos = pos_icebox2vpr(pos)
            g.routing.localnames.add(vpos, netname, track_node)
            logging.debug(
                " Setting local name %s on %s for %s",
                netname, vpos, track_fmt)


def add_edges(g, ic):
    for ipos in list(tiles(ic)):
        tile_type = ic.tile_type(*ipos)
        vpos = pos_icebox2vpr(ipos)

        # FIXME: If IO type, connect PACKAGE_PIN_I and PACKAGE_PIN_O manually...
##        if tile_type == "IO":
##            vpr_pio_pos = vpos
##            vpr_pin_pos = pos_icebox2vprpin(ipos)
##            print(tile_type, "pio:", ipos, vpos, "pin:", vpr_pin_pos)
##            if "EMPTY" in g.block_grid[vpr_pin_pos].block_type.name:
##                continue
##
##            print("PIO localnames:", g.routing.localnames[vpr_pio_pos])
##            print("PIN localnames:", g.routing.localnames[vpr_pin_pos])
##            for i in [0, 1]:
##                # pio -> pin
##                pio_iname = "O[{}]".format(i)
##                src_inode = g.routing.localnames[(vpr_pio_pos, pio_iname)]
##                pin_iname = "[{}]O[0]".format(i)
##                dst_inode = g.routing.localnames[(vpr_pin_pos, pin_iname)]
##                edgei = g.routing.create_edge_with_nodes(
##                    src_inode, dst_inode, switch=g.switches["short"])
##                print(vpr_pio_pos, pio_iname, format_node(g, src_inode),
##                      vpr_pin_pos, pin_iname, format_node(g, dst_inode),
##                      edgei)
##
##                # pin -> pio
##                pin_oname = "[{}]I[0]".format(i)
##                src_onode = g.routing.localnames[(vpr_pin_pos, pin_oname)]
##                pio_oname = "I[{}]".format(i)
##                dst_onode = g.routing.localnames[(vpr_pio_pos, pio_oname)]
##                edgeo = g.routing.create_edge_with_nodes(
##                    src_onode, dst_onode, switch=g.switches["short"])
##                print(vpr_pin_pos, pin_oname, format_node(g, src_onode),
##                      vpr_pio_pos, pio_oname, format_node(g, dst_onode),
##                      edgeo)

        for entry in ic.tile_db(*ipos):
            def skip(m, *args, level=logging.DEBUG, **kw):
                p = {
                    logging.DEBUG: logging.debug,
                    logging.WARNING: logging.warn,
                    logging.INFO: logging.info,
                }[level]
                p("On %s skipping entry %s: "+m, ipos, format_entry(entry), *args, **kw)

            if not ic.tile_has_entry(*ipos, entry):
                #skip('Non-existent edge!')
                continue

            switch_type = entry[1]
            if switch_type not in ("routing", "buffer"):
                skip('Unknown switch type %s', switch_type)
                continue

            src_localname = entry[2]
            dst_localname = entry[3]

            remaining = filter_track_names([(ipos, src_localname), (ipos, dst_localname)])
            if len(remaining) != 2:
                skip("Remaining %s", remaining)
                continue

            create_edge_with_names(
                g,
                src_localname, dst_localname,
                ipos, g.switches[switch_type],
                skip,
            )


def print_nodes_edges(g):
    print("Edges: %d (index: %d)" %
          (len(g.routing._xml_parent(graph.RoutingEdge)),
           len(g.routing.id2element[graph.RoutingEdge])))
    print("Nodes: %d (index: %d)" %
          (len(g.routing._xml_parent(graph.RoutingNode)),
           len(g.routing.id2element[graph.RoutingNode])))

# DEBUG:root:On PI(25,13) skipping entry [!B2[0],!B2[1],B2[2],!B3[0],!B3[2] buffer glb_netwk_0 ram/RCLK]: dst missing PV(27,15):glb_netwk_0 (glb_netwk_0) node X027Y002<|125|>X027Y035 => *PV(27,15):ram/RCLK* (ram/RCLK) node None
# DEBUG:root:On PV(27,16) for 72973 X027Y015_BLK_TL-RAM[74].RCLK[0]-R-PIN<
# DEBUG:root: Setting local name ram/RCLK on PV(27,16) for 72973 X027Y015_BLK_TL-RAM[74].RCLK[0]-R-PIN<
# DEBUG:root: Local name ram/RCLK same as hlc_name on PV(27,16) for 72973 X027Y015_BLK_TL-RAM[74].RCLK[0]-R-PIN<
def ram_pin_offset(pin):
    ram_pins_0to8 = ["WADDR[0]", "WCLKE[0]", "WCLK[0]", "WE[0]"]
    for i in range(8):
        ram_pins_0to8.extend([
            "RDATA[{}]".format(i),
            "MASK[{}]".format(i),
            "WDATA[{}]".format(i),
        ])
    ram_pins_0to8.extend(['WADDR[{}]'.format(i) for i in range(0, 11)])

    ram_pins_8to16 = ["RCLKE[0]", "RCLK[0]", "RE[0]"]
    for i in range(8,16):
        ram_pins_8to16.extend([
            "RDATA[{}]".format(i),
            "MASK[{}]".format(i),
            "WDATA[{}]".format(i),
        ])
    ram_pins_8to16.extend(['RADDR[{}]'.format(i) for i in range(0, 11)])

    if ic.device == '384':
        assert False, "384 device doesn't have RAM!"
    elif ic.device == '1k':
        top_pins = ram_pins_8to16
        bot_pins = ram_pins_0to8
    else:
        assert ic.device in ('5k', '8k'), "{} is unknown device".format(ic.device)
        top_pins = ram_pins_0to8
        bot_pins = ram_pins_8to16

    if pin.name in top_pins:
        return Offset(0, 1)
    elif pin.name in bot_pins:
        return Offset(0, 0)
    else:
        assert False, "RAM pin {} doesn't match name expected for metadata".format(pin.name)


def get_pin_meta(block, pin):
    grid_sz = PositionVPR(ic.max_x+1+4, ic.max_y+1+4)
    if "PIN" in block.block_type.name:
        if block.position.x == 1:
            return (graph.RoutingNodeSide.RIGHT, Offset(0, 0))
        elif block.position.y == 1:
            return (graph.RoutingNodeSide.TOP, Offset(0, 0))
        elif block.position.y == grid_sz.y-2:
            return (graph.RoutingNodeSide.BOTTOM, Offset(0, 0))
        elif block.position.x == grid_sz.x-2:
            return (graph.RoutingNodeSide.LEFT, Offset(0, 0))

    if "RAM" in block.block_type.name:
        return (graph.RoutingNodeSide.RIGHT, ram_pin_offset(pin))

    if "PIO" in block.block_type.name:
        if pin.name.startswith("O[") or pin.name.startswith("I["):
            if block.position.x == 2:
                return (graph.RoutingNodeSide.LEFT, Offset(0, 0))
            elif block.position.y == 2:
                return (graph.RoutingNodeSide.BOTTOM, Offset(0, 0))
            elif block.position.y == grid_sz.y-3:
                return (graph.RoutingNodeSide.TOP, Offset(0, 0))
            elif block.position.x == grid_sz.x-3:
                return (graph.RoutingNodeSide.RIGHT, Offset(0, 0))
        return (graph.RoutingNodeSide.RIGHT, Offset(0, 0))

    if "PLB" in block.block_type.name:
        if "FCIN" in pin.port_name:
            return (graph.RoutingNodeSide.BOTTOM, Offset(0, 0))
        elif "FCOUT" in pin.port_name:
            return (graph.RoutingNodeSide.TOP, Offset(0, 0))

        return (graph.RoutingNodeSide.RIGHT, Offset(0, 0))

    assert False, (block, pin)


def main(part, read_rr_graph, write_rr_graph):
    global ic

    print('Importing input g', part)
    ic, g = init(part, read_rr_graph)

    # my_test(ic, g)
    print('Source g loaded')
    print_nodes_edges(g)
    grid_sz = g.block_grid.size
    print("Grid size: %s" % (grid_sz, ))
    print()

    print('Clearing')
    print('='*80)
    print('Clearing nodes and edges')
    g.routing.clear()
    print('Clearing channels')
    g.channels.clear()
    print('Cleared original g')
    print_nodes_edges(g)
    print()
    print()
    print('Rebuilding block I/O nodes')
    print('='*80)

    g.create_block_pins_fabric(
        g.switches['__vpr_delayless_switch__'], get_pin_meta)
    print_nodes_edges(g)

    print()
    print('Adding pin aliases')
    print('='*80)
    add_pin_aliases(g, ic)

    segments = ic.group_segments(list(tiles(ic)))
    add_tracks(g, ic, segments, segtype_filter="local")
    add_tracks(g, ic, segments, segtype_filter="span4")
    add_tracks(g, ic, segments, segtype_filter="span12")
    add_global_tracks(g, ic)

    print()
    print('Adding edges')
    print('='*80)
    add_edges(g, ic)
    print()
    print_nodes_edges(g)
    print()
    print('Padding channels')
    print('='*80)
    dummy_segment = g.segments['dummy']
    g.pad_channels(dummy_segment.id)
    print()
    print('Saving')
    open(write_rr_graph, 'w').write(
        ET.tostring(g.to_xml(), pretty_print=True).decode('ascii'))
    print()
    print('Exiting')
    sys.exit(0)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--device', help='')
    parser.add_argument('--read_rr_graph', help='')
    parser.add_argument('--write_rr_graph', default='out.xml', help='')

    args = parser.parse_args()

    if args.verbose:
        loglevel=logging.DEBUG
    else:
        loglevel=logging.INFO
    logging.basicConfig(level=loglevel)

    mode = args.device.lower()[2:]
    main(mode, args.read_rr_graph, args.write_rr_graph)
