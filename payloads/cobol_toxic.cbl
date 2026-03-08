       IDENTIFICATION DIVISION.
       PROGRAM-ID. TOXIC-PANDORA.
       AUTHOR. PANDORA-SYSTEM.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-COUNTER PIC 9(9) VALUE 0.
       01 WS-MESSAGE PIC X(50) VALUE 
          "YOU HAVE BEEN POISONED BY PANDORA".
       
       PROCEDURE DIVISION.
       0000-MAIN.
           DISPLAY "╔══════════════════════════════════════╗"
           DISPLAY "║     💀 PANDORA TOXIC PAYLOAD 💀     ║"
           DISPLAY "╚══════════════════════════════════════╝"
           
       1000-INFINITE-LOOP.
           ADD 1 TO WS-COUNTER.
           DISPLAY "[" WS-COUNTER "] " WS-MESSAGE.
           
           IF WS-COUNTER > 99999999
               MOVE 0 TO WS-COUNTER
           END-IF.
           
           GO TO 1000-INFINITE-LOOP.
           
       9000-EXIT.
           STOP RUN.
