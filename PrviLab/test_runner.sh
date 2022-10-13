(
cd tests
for dir in ./*
do
	cd ..
	py GLA.py < ./tests/$dir/*.lan
	py ./analizator/LA.py < ./tests/$dir/*.in > ./outputs/"$dir".out
	cd ./tests
done)
