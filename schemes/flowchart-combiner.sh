#!/bin/bash


mmdc -i grid-flowchart.md -o grid-flowchart.png -t forest  -s 3
mmdc -i ic-flowchart-pre.md -o ic-flowchart-pre.png -t forest  -s 3 
mmdc -i ic-flowchart-prod.md -o ic-flowchart-prod.png -t forest  -s 3 


# layout='horizontal'
layout='vertical'
layout='split-vertical'

if [ "$layout" == "horizontal" ]; then
    
    convert grid-flowchart-1.png -gravity NorthWest -pointsize 40 -annotate +10+1 '(a) Grid Generation' grid-flowchart-2.png    
    montage grid-flowchart-2.png ic-flowchart-1.png -tile 1x -geometry +0+80 combined-flowcharts.tmp.png
    convert combined-flowcharts.tmp.png -gravity NorthWest -pointsize 40 -annotate +10+500 '(b) Initial Conditions' combined-flowcharts-${layout}.png
    rm grid-flowchart-1.png grid-flowchart-2.png ic-flowchart-1.png combined-flowcharts.tmp.png
    
    cp combined-flowcharts-${layout}.png ../figs/combined-flowcharts.png


elif [  "$layout" == "vertical" ]; then
    montage grid-flowchart-1.png ic-flowchart-pre-1.png ic-flowchart-prod-1.png -tile 3x1 -geometry +200+200 combined-flowcharts.tmp.png
    
    cnf="-gravity NorthWest -pointsize 100 -font Open-Sans-Extrabold"
    convert combined-flowcharts.tmp.png $cnf -annotate +1000+10 '(a) Grid Generation' combined-flowcharts.tmp-2.png    
    convert combined-flowcharts.tmp-2.png $cnf -annotate +3400+10 '(b) Initial Conditions (prep)' combined-flowcharts.tmp-3.png 
    convert combined-flowcharts.tmp-3.png $cnf -annotate +5600+10 '(c) Initial Conditions (prod)' combined-flowcharts-${layout}.png

    # rm grid-flowchart-1.png ic-flowchart-1.png combined-flowcharts.tmp.png combined-flowcharts.tmp-2.png
    
    cp combined-flowcharts-${layout}.png ../figs/combined-flowcharts.png

else
    montage ic-flowchart-pre-1.png ic-flowchart-prod-1.png -tile 2x1 -geometry +200+200 combined-flowcharts.tmp.png
    montage grid-flowchart-1.png -tile 1x1  -geometry +200+200 grid-flowchart.tmp.png    

    cnf="-gravity NorthWest -pointsize 100 -font Open-Sans-Extrabold"
    convert grid-flowchart.tmp.png $cnf -annotate +1000+10 'Grid Generation' grid-flowchart.png

    convert combined-flowcharts.tmp.png $cnf -annotate +800+10 '(a) Initial Conditions (prep)' combined-flowcharts.tmp-2.png 
    convert combined-flowcharts.tmp-2.png $cnf -annotate +3200+10 '(b) Initial Conditions (prod)' combined-icflowcharts-${layout}.png

    cp grid-flowchart.png ../figs/grid-flowchart.png
    cp combined-icflowcharts-${layout}.png ../figs/combined-icflowcharts.png


fi




