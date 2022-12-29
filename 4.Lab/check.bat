@echo off
(
cd tests
for /d %%f in (*) do (
	cd ..
	fc outputs\%%f.out tests\%%f\test.out
	cd .\tests
)
cd ..
)>output.txt
