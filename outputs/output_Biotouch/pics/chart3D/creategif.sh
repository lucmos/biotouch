convert -resize 768x576 -delay 5 -loop 0 `ls  *.png | sort -V` "$1"
