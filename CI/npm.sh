#!/bin/sh

echo ""
echo "NPM build JS and CSS"
echo ""
echo "Changing js/css files, please wait ..." 
begin=$(date +"%s")

echo ""
echo "Run npm to minimize the CSS and JS files"
cd sourcefiles
npm install
npm run build-css
npm run build-classic-js
npm run build-js
cd ..
git add -u
git add *
git commit -m "Minimize JS/CSS files"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Change time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast changing would be less than 1 minute."
echo ""
echo "NPM Done!"
echo ""
