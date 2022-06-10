# Place footprints console script
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import placefp'
#   To reapply:
#     import importlib
#     importlib.reload(placefp)
#  OR
#    exec(open("path-to-script-file").read())

import pcbnew
import math
import itertools


class Switch:
    # S, D, Q, RL, RP
    _pos = {"S": (0, 0), "D": (-3.4, 0), "Q": (3.4, 0), "RL": (8.3, 4), "RP": (8.3, -3)}

    def __init__(self, board, num) -> None:
        if not board and not num:
            return  # dummy
        self.footprints = {
            "S": board.FindFootprintByReference("S" + str(num)),
            "D": board.FindFootprintByReference("D" + str(num)),
            "Q": board.FindFootprintByReference("Q" + str(num)),
            "RL": board.FindFootprintByReference("RL" + str(num)),
            "RP": board.FindFootprintByReference("RP" + str(num)),
        }
        self.orient()

    def orient(self):
        self.footprints["S"].SetOrientation(0)  # 1/10 of degree
        self.footprints["D"].SetOrientation(-90 * 10)  # 1/10 of degree
        self.footprints["Q"].SetOrientation(90 * 10)  # 1/10 of degree
        self.footprints["RL"].SetOrientation(-90 * 10)  # 1/10 of degree
        self.footprints["RP"].SetOrientation(90 * 10)  # 1/10 of degree

    @staticmethod
    def add_track(start, end, layer=pcbnew.F_Cu):
        board = pcbnew.GetBoard()
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(start)
        track.SetEnd(end)
        track.SetWidth(int(0.3 * 1e6))
        track.SetLayer(layer)
        board.Add(track)

    def get_pad_point(self, fp, pad_num):
        return self.footprints[fp].FindPadByNumber(str(pad_num)).GetCenter()

    def get_track_end(self, fp, pad_num, dist):
        start = self.get_pad_point(fp, pad_num)
        deg = self.footprints[fp].GetOrientation() // 10
        d = dist * 1e6  # mm
        deg = 90 + deg
        return pcbnew.wxPoint(
            start.x + d * math.cos(math.radians(deg)),
            start.y - d * math.sin(math.radians(deg)),
        )

    def add_tracks(self):
        sta = self.get_pad_point("RL", 1)
        end = self.get_pad_point("RP", 1)
        Switch.add_track(sta, end)

        sta = self.get_pad_point("RP", 2)
        end = self.get_track_end("RP", 2, 2)
        Switch.add_track(sta, end)
        end2 = self.get_pad_point("Q", 1)
        Switch.add_track(end, end2)

        sta = self.get_pad_point("RL", 2)
        end = self.get_track_end("RL", 2, -7)
        Switch.add_track(sta, end)
        end2 = self.get_pad_point("D", 2)
        Switch.add_track(end, end2)

    def place(self, offset):
        for fp in self._pos.keys():
            p = pcbnew.wxPointMM(
                Switch._pos[fp][0] + offset[0], Switch._pos[fp][1] + offset[1]
            )
            self.footprints[fp].SetPosition(p)

    def rotate(self, deg):
        p = self.footprints["S"].GetPosition()
        for f, fp in self.footprints.items():
            fp.Rotate(p, deg * 10)


class Keyboard(object):
    def __init__(self) -> None:
        self.switches = [Switch(None, None)]
        board = pcbnew.GetBoard()
        for i in range(1, 76):
            self.switches.append(Switch(board, i))

    def place_footprints(self):
        dim = 19.05

        # row 1
        for i in range(1, 16):
            self.switches[i].place((i * dim, 0))
        # row 2
        offs = dim + dim / 4
        self.switches[16].place((offs, dim))
        for i in range(17, 29):
            self.switches[i].place((offs + dim / 4 + (i - 16) * dim, dim))
        self.switches[29].place((offs + dim / 4 + dim * 13 + dim / 4, dim))
        # row 3
        self.switches[31].place((dim / 2, 2 * dim))
        self.switches[32].place((3 * dim / 2 + dim / 8, 2 * dim))
        offs = 3 * dim / 2 + dim / 4
        for i in range(33, 44):
            self.switches[i].place((offs + (i - 32) * dim, 2 * dim))
        offs += 12 * dim + dim / 4
        self.switches[44].place((offs, 2 * dim))
        self.switches[45].place((offs + dim + dim / 4 + dim / 8, 2 * dim))
        # row 4
        offs = dim * (0.5 + 0.75 / 2)
        self.switches[46].place((offs, 3 * dim))
        offs += dim + dim * 0.75 / 2
        for i in range(47, 58):
            self.switches[i].place((offs + (i - 47) * dim, 3 * dim))
        offs += dim * 11
        self.switches[58].place((offs + dim / 8, 3 * dim))
        offs += dim * 1.25
        self.switches[59].place((offs, 3 * dim))
        self.switches[60].place((offs + dim, 3 * dim))
        # row 5
        for i in range(61, 64):
            self.switches[i].place((dim / 2 + (i - 61) * dim, 4 * dim))
        offs = dim / 2 + dim * 3
        self.switches[64].place((offs + dim / 8, 4 * dim))
        self.switches[65].place((offs + dim * 1.25 + dim / 8, 4 * dim))
        offs += dim * 1.25 * 2
        self.switches[66].place((offs, 4.5 * dim))
        self.switches[66].rotate(-15)
        offs += dim * 1.25
        self.switches[67].place((offs, 4 * dim))
        self.switches[30].place((offs, 5 * dim))
        self.switches[68].place((offs + dim + dim / 4, 4.5 * dim))
        self.switches[68].rotate(15)
        offs += dim * 1.25
        for i in range(69, 76):
            self.switches[i].place((offs + (i - 68) * dim, 4 * dim))

        board = pcbnew.GetBoard()
        tp1 = board.FindFootprintByReference("TP1")
        tp2 = board.FindFootprintByReference("TP2")
        tp1.SetPosition(pcbnew.wxPointMM(dim * 6.0, dim * 3.7))
        tp2.SetPosition(pcbnew.wxPointMM(dim * 6.2, dim * 3.7))

        bp = board.FindFootprintByReference("U1")
        bp.SetOrientation(90 * 10)  # 1/10 of degree
        bp.SetPosition(pcbnew.wxPointMM(dim * 1.29, dim))

        pcbnew.Refresh()

    def remove_tracks(self):
        # delete tracks first
        board = pcbnew.GetBoard()
        tracks = board.GetTracks()
        for t in tracks:
            board.Delete(t)

    def add_via(self, loc):
        board = pcbnew.GetBoard()
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(loc)
        via.SetDrill(int(0.3 * 1e6))
        via.SetWidth(int(0.6 * 1e6))
        board.Add(via)

    def via_track(self, sw, fp, pad_num, dir="down"):
        sta = sw.get_pad_point(fp, pad_num)
        end = sw.get_track_end(fp, pad_num, 2 if dir == "up" else -2)
        Switch.add_track(sta, end)
        self.add_via(end)
        yval = end.y + 4 * 1e6 if dir == "down" else end.y - 4 * 1e6
        end2 = pcbnew.wxPoint(end.x, yval)
        Switch.add_track(end, end2, pcbnew.B_Cu)
        return end2

    def add_tracks(self):
        self.remove_tracks()
        # add tracks
        for i in range(1, 76):
            self.switches[i].add_tracks()

        # rows
        for i in itertools.chain(
            range(1, 15),
            range(16, 29),
            range(31, 45),
            range(46, 60),
            range(61, 65),
            range(69, 75),
        ):
            sw1 = self.switches[i]
            sw2 = self.switches[i + 1]
            sta = sw1.get_pad_point("RP", 2)
            end = pcbnew.wxPoint(sta.x + 11 * 1e6, sta.y)
            Switch.add_track(sta, end)
            end2 = sw2.get_pad_point("Q", 1)
            Switch.add_track(end, end2)

        # columns
        for i1, i2, i3, i4, i5 in zip(
            range(1, 16),
            range(16, 31),
            range(31, 46),
            range(46, 61),
            range(61, 76),
        ):
            for st, en in [(i1, i2), (i2, i3), (i3, i4), (i4, i5)]:
                if st in [1, 16, 15, 30]:
                    continue
                start = self.via_track(self.switches[st], "RL", 1, "down")
                end = self.via_track(self.switches[en], "RP", 1, "up")
                Switch.add_track(start, end, pcbnew.B_Cu)

        # ground
        for i in range(1, 76):
            sta = self.switches[i].get_pad_point("Q", 2)
            end = self.switches[i].get_track_end("Q", 2, -1.5)
            Switch.add_track(sta, end)
            self.add_via(end)
            sta = self.switches[i].get_pad_point("D", 1)
            end = self.switches[i].get_track_end("D", 1, -1.5)
            Switch.add_track(sta, end)
            self.add_via(end)

        pcbnew.Refresh()


kb = Keyboard()
kb.place_footprints()
kb.add_tracks()
