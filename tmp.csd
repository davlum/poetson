<CsoundSynthesizer>

<CsOptions>

--output=dac --midi-device=a --nodisplays

</CsOptions>

<CsInstruments>

sr = 44100
ksmps = 64
nchnls = 2
0dbfs = 1.0
 massign 0, 19
gargg0 init 0.0
girgfree_vco = 101
ir15 = girgfree_vco
ir17 vco2init 1, ir15
girgfree_vco = ir17
giPort init 1
opcode FreePort, i, 0
xout giPort
giPort = giPort + 1
endop




instr 22

endin

instr 21
 event_i "i", 20, 604800.0, 1.0e-2
endin

instr 20
ir1 = 19
ir2 = 0.0
 turnoff2 ir1, ir2, ir2
ir5 = 18
 turnoff2 ir5, ir2, ir2
 exitnow 
endin

instr 19
ar0 = gargg0
ir3 active p1
ar1 upsamp k(ir3)
ar2 = sqrt(ar1)
ar1 = (1.0 / ar2)
if (ir3 < 2.0) then
    ar2 = 1.0
else
    ar2 = ar1
endif
kr0 linseg 0.0, 0.1, 1.0, 1.0, 1.0
ar1 upsamp kr0
kr0 linsegr 1.0, 1.0, 1.0, 0.5, 0.0
ar3 upsamp kr0
ar4 = (ar1 * ar3)
ar1 = (0.25 * ar4)
ir11 ampmidi 1.0
ar3 upsamp k(ir11)
ar4 = (ar1 * ar3)
ir13 = 1.0
ir14 cpsmidi 
kr0 vco2ft ir14, 0
ar1 oscilikt ir13, ir14, kr0
ar3 = (ar4 * ar1)
ar1 = (ar2 * ar3)
ar2 = (ar0 + ar1)
gargg0 = ar2
endin

instr 18
ar0 = gargg0
gargg0 = 0.0
arl0 init 0.0
arl1 init 0.0
ar1 = (0.75 * ar0)
ir10 = 0.6
ir11 = 12000.0
ar2, ar3 reverbsc ar0, ar0, ir10, ir11
ar4 = (ar0 + ar2)
ar2 = (0.25 * ar4)
ar4 = (ar1 + ar2)
ir17 = 1.0
ar2 upsamp k(ir17)
ir18 = 0.0
ir19 = 90.0
ir20 = 100.0
ar5 compress ar4, ar2, ir18, ir19, ir19, ir20, ir18, ir18, 0.0
ar4 = (ar5 * 0.8)
arl0 = ar4
ar4 = (ar0 + ar3)
ar0 = (0.25 * ar4)
ar3 = (ar1 + ar0)
ar0 compress ar3, ar2, ir18, ir19, ir19, ir20, ir18, ir18, 0.0
ar1 = (ar0 * 0.8)
arl1 = ar1
ar0 = arl0
ar1 = arl1
 outs ar0, ar1
endin

</CsInstruments>

<CsScore>



f0 604800.0

i 22 0.0 -1.0 
i 21 0.0 -1.0 
i 18 0.0 -1.0 

</CsScore>



</CsoundSynthesizer>