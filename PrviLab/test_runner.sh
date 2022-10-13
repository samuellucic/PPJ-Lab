(
cd tests
for dir in ./*
do
	echo $dir
	cd ..
	path=$(echo $dir| cut -c 3-)
	echo $SUBSTRING
	py GLA.py < ./tests/$path/test.lan
	py ./analizator/LA.py < ./tests/$path/test.in > ./outputs/"$path".out
	cd ./tests
done)
