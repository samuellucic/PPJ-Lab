(
cd tests
for dir in ./*
do
	cd ..
	path=$(echo $dir| cut -c 3-)
	printf "\n----------\n$path\n----------\n"
	py GeneratorKoda.py < ./tests/$path/test.in
	node.exe main.js a.frisc > ./outputs/"$path".out
	cd ./tests
done)
