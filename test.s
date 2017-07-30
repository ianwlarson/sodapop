;
; Test assembly file
;
;

    xor     $t3, $t3, $t3
double_top:
    bgtz    $t3, end
    xor     $t0, $t0, $t0
    addi    $t1, $zero, 0x1
    addi    $t2, $zero, 0x100
top:
    add     $t0, $t0, $t1
    bne     $t0, $t2, top
    add     $t3, $t3, $t1
    beq     $t3, $t1, double_top
end:
    beq     $t0, $t0, end