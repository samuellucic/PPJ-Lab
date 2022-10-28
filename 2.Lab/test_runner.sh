(
cd tests
for dir in ./*
do
	cd ..
	path=$(echo $dir| cut -c 3-)
	printf "\n----------\n$path\n----------\n"
	py GSA.py < ./tests/$path/test.san
	cd ./analizator
	py SA.py < ../tests/$path/test.in > ../outputs/"$path".out
	cd ..
	cd ./tests
done)
