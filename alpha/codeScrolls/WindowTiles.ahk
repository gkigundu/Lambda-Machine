; Author : Derek Maier

#NoEnv
#persistent
#SingleInstance force
SendMode Input
SetWorkingDir %A_ScriptDir%

;----------------------------------------
SysGet, Mon1, MonitorWorkArea , 1 
Mon1Width 			:= Abs(Mon1Right - Mon1Left)
Mon1Height 			:= Abs(Mon1Bottom - Mon1Top)
Mon1Widthhalf 		:= Ceil(Abs(Mon1Width) / 2)
Mon1Heighthalf 		:= Ceil(Abs(Mon1Height) / 2)
Mon1WidthMiddle 	:= Mon1Left + Abs(Mon1Widthhalf)
Mon1HeightMiddle 	:= Mon1Top + Abs(Mon1Heighthalf)

SysGet, Mon2, Monitor, 2 
Mon2Width 			:= Abs(Mon2Right - Mon2Left)
Mon2Height 			:= Abs(Mon2Bottom - Mon2Top)
Mon2Widthhalf 		:= Ceil(Abs(Mon2Width) / 2)
Mon2Heighthalf 		:= Ceil(Abs(Mon2Height) / 2)
Mon2WidthMiddle 	:= Mon2Left + Abs(Mon2Widthhalf)
Mon2HeightMiddle 	:= Mon2Top + Abs(Mon2Heighthalf)

;msgbox, %Mon2WidthMiddle%  x  %Mon2HeightMiddle%

;----------------------------------------

^esc::ExitApp
^+r::reload

;----------------------------------------

^space::run "C:\Users\%user%\Google Drive"
^d::run "C:\Users\%user%\Downloads"
^f1::run nircmd monitor off

;----------------------------------------

^!z::									
	WinRestore, a
	WinMove,A,,200,45,964,690
	return

;	Screen 1
#z::	
	WinRestore, a
	WinMove,A,,%Mon1Left%,%Mon1Top%,%Mon1Widthhalf%,%Mon1Height%
	return	
#x::	
	WinRestore, a
	WinMove,A,,%Mon1WidthMiddle%,%Mon1Top%,%Mon1Widthhalf%,%Mon1Height%
	return				
!a::								
	WinRestore, a
	WinMove,A,,%Mon1Left%,%Mon1Top%,%Mon1Widthhalf%,%Mon1Heighthalf%	
	return
!s::									
	WinRestore, a
	WinMove,A,,%Mon1WidthMiddle%,%Mon1Top%,%Mon1Widthhalf%,%Mon1Heighthalf%	
	return
!z::
	WinRestore, a
	WinMove,A,,%Mon1Left%,%Mon1HeightMiddle%,%Mon1Widthhalf%,%Mon1Heighthalf%	
	return
!x::									
	WinRestore, a
	WinMove,A,,%Mon1WidthMiddle%,%Mon1HeightMiddle%,%Mon1Widthhalf%,%Mon1Heighthalf%	
	return
	
;	Screen 2
#+z::	
	WinRestore, a
	WinMove,A,,%Mon2Left%,%Mon2Top%,%Mon2Widthhalf%,%Mon2Height%
	return	
#+x::	
	WinRestore, a
	WinMove,A,,%Mon2WidthMiddle%,%Mon2Top%,%Mon2Widthhalf%,%Mon2Height%
	return				
!+a::								
	WinRestore, a
	WinMove,A,,%Mon2Left%,%Mon2Top%,%Mon2Widthhalf%,%Mon2Heighthalf%	
	return
!+s::									
	WinRestore, a
	WinMove,A,,%Mon2WidthMiddle%,%Mon2Top%,%Mon2Widthhalf%,%Mon2Heighthalf%	
	return
!+z::
	WinRestore, a
	WinMove,A,,%Mon2Left%,%Mon2HeightMiddle%,%Mon2Widthhalf%,%Mon2Heighthalf%	
	return
!+x::									
	WinRestore, a
	WinMove,A,,%Mon2WidthMiddle%,%Mon2HeightMiddle%,%Mon2Widthhalf%,%Mon2Heighthalf%	
	return
