(
cd tests
for dir in ./*
do
	cd ..
	path=$(echo $dir| cut -c 3-)
	printf "\n----------\n$path\n----------\n"
	py GLA.py < ./tests/$path/test.lan
	cd ./analizator
	py LA.py < ../tests/$path/test.in > ../outputs/"$path".out
	cd ..
	cd ./tests
done)
