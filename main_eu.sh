#Pasos:
#Simple:
#En corpus/eu/ErreXail/sinpleak/*(200) (Simple)
#Complejo:
#En corpus/eu/ErreXail/konplexuak/*(200) (Complejo)
#OBTENER MULTIAZTERTEST EN 5 EN 5
function obtenerdatossimple5en5()
{
#simple
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/eu/ErreXail/sinpleak"
#voy a dividir los ficheros en 5 en 5
cd $dir
has=1
buk=5
for j in `seq 1 40`
do
	mkdir $buk
	for i in `seq $has $buk`
	do
       		cp corp_zernola_$i.trc.txt $buk/Texto_$i.txt
	done
        has=$(echo "$has+5" | bc -l)
        buk=$(echo "$buk+5" | bc -l)
done
}


function obtenerdatoscomplejo5en5()
{
#complejo
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/eu/ErreXail/konplexuak"
cd $dir
#i=1
#for text in `ls  $dir`
#do
#  mv $text Texto_$i.txt
#  i=$(echo "$i+1" | bc -l)
#done
#voy a dividir los ficheros en 5 en 5
has=1
buk=5
for j in `seq 1 40`
do
	mkdir $buk
	for i in `seq $has $buk`
	do
       		cp Texto_$i.txt $buk
	done
        has=$(echo "$has+5" | bc -l)
        buk=$(echo "$buk+5" | bc -l)
done
}
function obtenerdatosmultiaztertest_eu()
{
modelo=$1
cd /media/datos/Dropbox/ikerkuntza/metrix-env
source bin/activate
cd /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual
#ANALIZA SI PROCESA BIEN (Por ejemplo hay que separar "-" de las palabras con espacio)
#python3 ./multiaztertest.py -s -c -r -f  $dir/5/Texto_1.txt -l basque -m stanford -d "/home/kepa"
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/eu/ErreXail/sinpleak"
for i in 5 #`seq 5 5 200`
do
     	python3 multiaztertest.py -s -c -r -f  $dir/$i/*.txt -l basque -m $modelo -d "/home/kepa"
done


#complejo multiaztertest
#python3 ./multiaztertest.py -s -c -r -f  $dir/55/Texto_53.txt -l basque -m stanford -d "/home/kepa"
#dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/eu/ErreXail/konplexuak"
#for i in `seq 5 5 200`
#do
#     	python3 multiaztertest.py -s -c -r -f  $dir/$i/*.txt -l basque -m $modelo -d "/home/kepa"
#done
}

function cross10banatu_es()
{
modelo=$1
echo "Genera un train y un test balanceado simple-complejo test(05simple  y 55complejo el resto train"
#output:/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/[train|test]
#test:
#input1: /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/simple/5/results/full_results_aztertest_withlevel.csv +
#input2: /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/complejo/55/results/full_results_aztertest_withlevel.csv

#Añade el nivel
#crea el fichero a concatenar
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/simple"
echo -e "level\n0\n0\n0\n0\n0\n" > $dir/simplelevel.txt
for i in `seq 5 5 50`
do
	paste -d',' $dir/$i/results/full_results_aztertest.csv $dir/simplelevel.txt > $dir/$i/results/full_results_aztertest_withlevel.csv
        head -n 6 $dir/$i/results/full_results_aztertest_withlevel.csv > $dir/$i/results/full_results_aztertest_withlevelgarbi.csv
	tail -n +2 $dir/$i/results/full_results_aztertest_withlevelgarbi.csv > $dir/$i/results/full_results_aztertest_withlevelsincab.csv
done
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/complejo"
#crea el fichero a concatenar
echo -e "level\n1\n1\n1\n1\n1\n" > $dir/complejolevel.txt
for i in `seq 55 5 100`
do
	paste -d',' $dir/$i/results/full_results_aztertest.csv $dir/complejolevel.txt > $dir/$i/results/full_results_aztertest_withlevel.csv
        head -n 6 $dir/$i/results/full_results_aztertest_withlevel.csv > $dir/$i/results/full_results_aztertest_withlevelgarbi.csv
	tail -n +2 $dir/$i/results/full_results_aztertest_withlevelgarbi.csv > $dir/$i/results/full_results_aztertest_withlevelsincab.csv
done
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo"

for i in `seq 1 10`
do
        mkdir -p $dir/cross10$modelo/cross$i
        j=`expr $i \* 5`
        k=`expr $j + 50`
        cat $dir/simple/$j/results/full_results_aztertest_withlevelsincab.csv $dir/complejo/$k/results/full_results_aztertest_withlevelsincab.csv > $dir/cross10$modelo/cross$i/test_sincab.csv
done
cd $dir/cross10$modelo
cat cross1/test_sincab.csv cross2/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv > cross10/train_sincab.csv
cat cross1/test_sincab.csv cross2/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross10/test_sincab.csv > cross9/train_sincab.csv
cat cross1/test_sincab.csv cross2/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross8/train_sincab.csv
cat cross1/test_sincab.csv cross2/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross7/train_sincab.csv
cat cross1/test_sincab.csv cross2/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross6/train_sincab.csv
cat cross1/test_sincab.csv cross2/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross5/train_sincab.csv
cat cross1/test_sincab.csv cross2/test_sincab.csv cross3/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross4/train_sincab.csv
cat cross1/test_sincab.csv cross2/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross3/train_sincab.csv
cat cross1/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross2/train_sincab.csv
cat cross2/test_sincab.csv cross3/test_sincab.csv cross4/test_sincab.csv cross5/test_sincab.csv cross6/test_sincab.csv cross7/test_sincab.csv cross8/test_sincab.csv cross9/test_sincab.csv cross10/test_sincab.csv > cross1/train_sincab.csv
# #GEHITU BURUAK!!!!
#Lortu burua
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo"
head -n 1 $dir/simple/5/results/full_results_aztertest_withlevel.csv > $dir/burua.csv
for i in `seq 1 10`
do
        cat $dir/burua.csv $dir/cross10$modelo/cross$i/train_sincab.csv > $dir/cross10$modelo/cross$i/train_cab.csv
        cat $dir/burua.csv $dir/cross10$modelo/cross$i/test_sincab.csv > $dir/cross10$modelo/cross$i/test_cab.csv
done
# #Crear 10-fold cross-validation formando 10 carpetas (1 a 10 ) con 5 ficheros simples y 5 complejos (1 con 51(50+1), 2 con 52(50+2)) para que quede todo balanceado.

WEKA_PATH=/home/kepa/weka-3-8-3
export CLASSPATH=$CLASSPATH:/home/kepa/weka-3-8-3/weka.jar #:/usr/share/java/libsvm.jar:/usr/share/java
CP="$CLASSPATH:/usr/share/java/"
#arrancar weka online
#java -cp $CP -Xmx1024m weka.gui.explorer.Explorer
#convertir csv en arff
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo"
for i in `seq 1 10`
do
	java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.core.converters.CSVLoader $dir/cross10$modelo/cross$i/train_cab.csv > $dir/cross10$modelo/cross$i/train_cab.arff
	java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.core.converters.CSVLoader $dir/cross10$modelo/cross$i/test_cab.csv > $dir/cross10$modelo/cross$i/test_cab.arff
done
#convierte la clase en nominal para poder ejecutar smo
for i in `seq 1 10`
do
# # # # Convert your class attribute(s) to nominal type. (Otherwise most classifiers will be disabled). If the class attribute is numeric, then click Filter choose filters->unsupervised->attribute->NumericToNominal.
	java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.filters.unsupervised.attribute.NumericToNominal -R last -i $dir/cross10$modelo/cross$i/train_cab.arff  -o $dir/cross10$modelo/cross$i/train_cab.nominal.arff
	java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.filters.unsupervised.attribute.NumericToNominal -R last -i $dir/cross10$modelo/cross$i/test_cab.arff -o $dir/cross10$modelo/cross$i/test_cab.nominal.arff
done

}
function crosswekafs_es()
{
modelo=$1
############################################################################
##FEATURE SELECTION:## We have tested chi square using different set of attributes: 25, 50, 75 and 100. 
########################################################################
WEKA_PATH=/home/kepa/weka-3-8-3
export CLASSPATH=$CLASSPATH:/home/kepa/weka-3-8-3/weka.jar #:/usr/share/java/libsvm.jar:/usr/share/java
CP="$CLASSPATH:/usr/share/java/"
N=5
CLASE=6
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo"
i=1
# ##Chi
#General options:-h 	Get help on available options.
#-i <filename> The file containing first input instances.
#-o <filename> The file first output instances will be written to.
#-r <filename> The file containing second input instances.
#-s <filename> The file second output instances will be written to.
#-c <class index> The number of the attribute to use as the class."first" and "last" are also valid entries. If not supplied then no class is assigned.
#-decimal <integer> The maximum number of digits to print after the decimal place for numeric values (default: 6)
#weka.filters.supervised.attribute.AttributeSelection
#weka.attributeSelection.ChiSquaredAttributeEval
#weka.attributeSelection.Ranker -T -1.7976931348623157E308 -N -1
java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.filters.supervised.attribute.AttributeSelection \
    -E "weka.attributeSelection.CfsSubsetEval -M" \
    -S "weka.attributeSelection.BestFirst -D 1 -N 5" \
    -b \
    -i /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/train_cab.nominal.arff \
    -o /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/train_cab.nominal.fs.arff \
    -r /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/test_cab.nominal.arff \
    -s /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/test_cab.nominal.fs.arff \
    -c last

#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.filters.supervised.attribute.AttributeSelection \
#    -E "weka.attributeSelection.ChiSquaredAttributeEval" \
#    -S "weka.attributeSelection.Ranker" \
#    -b \
#    -i /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/train_cab.nominal.arff \
#    -o /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/train_cab.nominal.fs.arff \
#    -r /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/test_cab.nominal.arff \
#    -s /media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo/cross10$modelo/cross1/test_cab.nominal.fs.arff
#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.filters.supervised.attribute.AttributeSelection -S "weka.attributeSelection.Ranker" -E "weka.attributeSelection.ChiSquaredAttributeEval" -i $dir/cross10$modelo/cross$i/train_cab.nominal.arff -o $dir/cross10$modelo/cross$i/train_cab.nominal.fs.arff -c last -decimal 6

#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.filters.supervised.attribute.AttributeSelection -S "weka.attributeSelection.Ranker -T -1.7976931348623157e308 -N $N" -E "weka.attributeSelection.ChiSquaredAttributeEval" -b -i $dir/cross10$modelo/cross$i/train_cab.nominal.arff -o $dir/cross10$modelo/cross$i/train_cab.nominal.fs.arff -r $dir/cross10$modelo/cross$i/test_cab.nominal.arff -s $dir/cross10$modelo/cross$i/test_cab.nominal.fs.arff -c last
####################################################################################
}

function crosswekasmodefault_es()
{
modelo=$1
# #python3 aztertest_dataset.py
# #MIRAR!!!!! /media/datos/Dropbox/ikerkuntza/UZ/programak/main.sh
###########################################################################
##TRAINING AND TESTING  WITH DEFAULT PARAMETERS
########################################################################
#General options:   -c last --illegal-access=warn
#-synopsis or -info Output synopsis for classifier (use in conjunction  with -h)
#-t <name of training file> Sets training file.
#-T <name of test file> Sets test file. If missing, a cross-validation will be performed on the training data.
#-c <class index> Sets index of class attribute (default: last).
#-x <number of folds> Sets number of folds for cross-validation (default: 10).
#-no-cv Do not perform any cross validation.
#-force-batch-training Always train classifier in batch mode, never incrementally.
#-split-percentage <percentage> Sets the percentage for the train/test set split, e.g., 66.
#-preserve-order Preserves the order in the percentage split.
#-s <random number seed> Sets random number seed for cross-validation or percentage split (default: 1).
#-m <name of file with cost matrix> Sets file with cost matrix.
#-toggle <comma-separated list of evaluation metric names>Comma separated list of metric names to toggle in the output.	All metrics are output by default with the exception of 'Coverage' and 'Region size'.	Available metrics:Correct,Incorrect,Kappa,Total cost,Average cost,KBrelative,KB information,	Correlation,Complexity 0,Complexity scheme,Complexity improvement,MAE,RMSE,RAE,RRSE,Coverage,Region size,TP rate,FP rate,Precision,Recall,F-measure,MCC,ROC area,PRC area
#-l <name of input file> Sets model input file. In case the filename ends with '.xml', 	a PMML file is loaded or, if that fails, options are loaded	from the XML file.
#-d <name of output file> Sets model output file. In case the filename ends with '.xml', only the options are saved to the XML file, not the model.
#-v 	Outputs no statistics for training data.
#-o 	Outputs statistics only, not the classifier.
#-output-models-for-training-splits Output models for training splits if cross-validation or percentage-split evaluation is used.
#-do-not-output-per-class-statistics 	Do not output statistics for each class.
#-k 	Outputs information-theoretic statistics.
#-classifications "weka.classifiers.evaluation.output.prediction.AbstractOutput + options" Uses the specified class for generating the classification output. 	E.g.: weka.classifiers.evaluation.output.prediction.PlainText
#-p range Outputs predictions for test instances (or the train instances if no test instances provided and -no-cv is used), along with the 	attributes in the specified range (and nothing else). Use '-p 0' if no attributes are desired.Deprecated: use "-classifications ..." instead.
#-distribution 	Outputs the distribution instead of only the prediction in conjunction with the '-p' option (only nominal classes). 	Deprecated: use "-classifications ..." instead.
#-r Only outputs cumulative margin distribution.
#-xml filename | xml-string Retrieves the options from the XML-data instead of the command line.
#-threshold-file <file> The file to save the threshold data to. The format is determined by the extensions, e.g., '.arff' for ARFF format or '.csv' for CSV.
#-threshold-label <label> The class label to determine the threshold data for (default is the first label) 
#-no-predictions Turns off the collection of predictions in order to conserve memory.



#Options specific to weka.classifiers.functions.SMO:-C 1.0 -L 0.001 -P 1.0e-12 -N 0 -V -1 -W 1 -K
#-no-checks (default: checks on)
#-C <double> The complexity constant C. (default 1)
#-N 	Whether to 0=normalize/1=standardize/2=neither. (default 0=normalize)
#-L <double> The tolerance parameter. (default 1.0e-3)
#-P <double> The epsilon for round-off error. (default 1.0e-12)
#-M Fit calibration models to SVM outputs. 
#-V <double>	The number of folds for the internal cross-validation. (default -1, use training data)
#-W <double> The random number seed. (default 1)
#-K <classname and parameters> 	The Kernel to use. (default: weka.classifiers.functions.supportVector.PolyKernel)
#-calibrator <scheme specification> Full name of calibration model, followed by options.(default: "weka.classifiers.functions.Logistic")
#-output-debug-info If set, classifier is run in debug mode and may output additional info to the console
#-do-not-check-capabilities If set, classifier capabilities are not checked before classifier is built (use with caution). 
#-num-decimal-places The number of decimal places for the output of numbers in the model (default 2).
#-batch-size The desired batch size for batch prediction  (default 100).


#Options specific to kernel weka.classifiers.functions.supportVector.PolyKernel:
#-E <num> 	The Exponent to use. 	(default: 1.0)
#-L 	Use lower-order terms. 	(default: no)
#-C <num> The size of the cache (a prime number), 0 for full cache and  -1 to turn it off. (default: 250007)
#-output-debug-info Enables debugging output (if available) to be printed. (default: off)

#Options specific to calibrator weka.classifiers.functions.Logistic:
#-C Use conjugate gradient descent rather than BFGS updates.
#-R <ridge> Set the ridge in the log-likelihood.
#-M <number> Set the maximum number of iterations (default -1, until convergence).
# -output-debug-info 	If set, classifier is run in debug mode and may output additional info to the console
#-do-not-check-capabilities 	If set, classifier capabilities are not checked before classifier is built (use with caution).
#-num-decimal-places The number of decimal places for the output of numbers in the model (default 4).
#-batch-size The desired batch size for batch prediction  (default 100).
#auto cross weka sin balancear
#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.classifiers.functions.SMO -C 1.0 -L 0.001 -P 1.02e-12 -N 0 -V -1 -W 1 -K "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007" -calibrator "weka.classifiers.functions.Logistic -R 1.0e-8 -M -1 -num-decimal-places 4" -t $dir/cross10$modelo/cross$i/train_cab.nominal.arff -d $dir/cross10$modelo/etrain.model -x 10 -o -c last > $dir/cross10$modelo/cross10results.txt
######################################################
#generate train model and test cross-10 banaceado:
###########################################################
WEKA_PATH=/home/kepa/weka-3-8-3
export CLASSPATH=$CLASSPATH:/home/kepa/weka-3-8-3/weka.jar #:/usr/share/java/libsvm.jar:/usr/share/java
CP="$CLASSPATH:/usr/share/java/"
dir="/media/datos/Dropbox/ikerkuntza/metrix-env/multilingual/corpus/es/simplecomplejo"
for i in `seq 1 10`
do
java --add-opens=java.base/java.lang=ALL-UNNAMED -cp $CP -Xmx1024m weka.classifiers.functions.SMO -C 1.0 -L 0.001 -P 1.02e-12 -N 0 -V -1 -W 1 -K "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007" -calibrator "weka.classifiers.functions.Logistic -R 1.0e-8 -M -1 -num-decimal-places 4" -t $dir/cross10$modelo/cross$i/train_cab.nominal.arff -d $dir/cross10$modelo/cross$i/etrain.model -c last > $dir/cross10$modelo/cross$i/train_output.txt
#test model
#-l model input file
#-c class index
#-T testfile
java --add-opens=java.base/java.lang=ALL-UNNAMED -cp $CP -Xmx1024m weka.classifiers.functions.SMO -c last -l $dir/cross10$modelo/cross$i/etrain.model -T $dir/cross10$modelo/cross$i/test_cab.nominal.arff -o > $dir/cross10$modelo/cross$i/test_statiticsoutput.txt
java --add-opens=java.base/java.lang=ALL-UNNAMED -cp $CP -Xmx1024m weka.classifiers.functions.SMO -c last -l $dir/cross10$modelo/cross$i/etrain.model -T $dir/cross10$modelo/cross$i/test_cab.nominal.arff -p 0 > $dir/cross10$modelo/cross$i/test_output.txt
done

for i in `seq 1 10`
do
less $dir/cross10$modelo/cross$i/test_output.txt | tail -n+6 | tr ' ' '@'|tr '+' '@'| sed 's/@@@@@@@@/ /g'| sed 's/@@@@@@@/ /g'|sed 's/@@@//g'|sed 's/@//g'|cut -f3 -d' '|cut -f2 -d:>$dir/cross10$modelo/cross$i/test_gold.txt
less $dir/cross10$modelo/cross$i/test_output.txt | tail -n+6 | tr ' ' '@'|tr '+' '@'| sed 's/@@@@@@@@/ /g'| sed 's/@@@@@@@/ /g'|sed 's/@@@//g'|sed 's/@//g'|cut -f4 -d' '|cut -f2 -d:>$dir/cross10$modelo/cross$i/test_predict.txt

paste $dir/cross10$modelo/cross$i/test_gold.txt $dir/cross10$modelo/cross$i/test_predict.txt > $dir/cross10$modelo/cross$i/compare.txt
#C= Correct detect; E= Error in predict ya que todos los errores son iguales (tienen el mismo coste)
C1=`less $dir/cross10$modelo/cross$i/compare.txt | grep -P '1\t1' |wc -l`
C2=`less $dir/cross10$modelo/cross$i/compare.txt | grep -P '0\t0' |wc -l`
E1=`less $dir/cross10$modelo/cross$i/compare.txt | grep -P '0\t1' |wc -l`
E2=`less $dir/cross10$modelo/cross$i/compare.txt | grep -P '1\t0' |wc -l`
C=`expr $C1 + $C2`
E=`expr $E1 + $E2`
T=`expr $C + $E`
Acc=$(bc <<< "scale=10;$C/$T")
printf "C:%d\tE:%d\tAcc:%s\n " $C $E $Acc > $dir/cross10$modelo/cross$i/emaitza.test.txt
done
cross10kalkulatu $dir/cross10$modelo emaitza.test.txt
}


function cross10kalkulatu()
{
#Media=0,5277777777
#La desviación estándar (σ) mide cuánto se separan los datos. es la raíz cuadrada de la varianza
#Varianza=σ2=0,0314
#Desviación estándar=σ = √0,0314= 0,17
#Así que usando la desviación estándar tenemos una manera "estándar" de saber qué es normal, o extra grande o extra pequeño. Media+/-Desviación estándar = (0,3505369105,0,7050186449) Cross9 es extra pequeño y cross6 extra grande
dir=$1
file=$2
#C:4	E:2	M:6	P:0.6666666666	R:0.4000000000	F:0.4999999999
C1=`less $dir/cross1/$file | cut -f1 |cut -f2 -d":" `
C2=`less $dir/cross2/$file | cut -f1 |cut -f2 -d":" `
C3=`less $dir/cross3/$file | cut -f1 |cut -f2 -d":" `
C4=`less $dir/cross4/$file | cut -f1 |cut -f2 -d":" `
C5=`less $dir/cross5/$file | cut -f1 |cut -f2 -d":" `
C6=`less $dir/cross6/$file | cut -f1 |cut -f2 -d":" `
C7=`less $dir/cross7/$file | cut -f1 |cut -f2 -d":" `
C8=`less $dir/cross8/$file | cut -f1 |cut -f2 -d":" `
C9=`less $dir/cross9/$file | cut -f1 |cut -f2 -d":" `
C10=`less $dir/cross10/$file | cut -f1 |cut -f2 -d":" `

C=`expr $C1 + $C2 + $C3 + $C4 + $C5 + $C6 + $C7 + $C8 + $C9 + $C10`

E1=`less $dir/cross1/$file | cut -f2 |cut -f2 -d":" `
E2=`less $dir/cross2/$file | cut -f2 |cut -f2 -d":" `
E3=`less $dir/cross3/$file | cut -f2 |cut -f2 -d":" `
E4=`less $dir/cross4/$file | cut -f2 |cut -f2 -d":" `
E5=`less $dir/cross5/$file | cut -f2 |cut -f2 -d":" `
E6=`less $dir/cross6/$file | cut -f2 |cut -f2 -d":" `
E7=`less $dir/cross7/$file | cut -f2 |cut -f2 -d":" `
E8=`less $dir/cross8/$file | cut -f2 |cut -f2 -d":" `
E9=`less $dir/cross9/$file | cut -f2 |cut -f2 -d":" `
E10=`less $dir/cross10/$file | cut -f2 |cut -f2 -d":" `

E=`expr $E1 + $E2 + $E3 + $E4 + $E5 + $E6 + $E7 + $E8 + $E9 + $E10`

A1=`less $dir/cross1/$file | cut -f3 |cut -f2 -d":" `
A2=`less $dir/cross2/$file | cut -f3 |cut -f2 -d":" `
A3=`less $dir/cross3/$file | cut -f3 |cut -f2 -d":" `
A4=`less $dir/cross4/$file | cut -f3 |cut -f2 -d":" `
A5=`less $dir/cross5/$file | cut -f3 |cut -f2 -d":" `
A6=`less $dir/cross6/$file | cut -f3 |cut -f2 -d":" `
A7=`less $dir/cross7/$file | cut -f3 |cut -f2 -d":" `
A8=`less $dir/cross8/$file | cut -f3 |cut -f2 -d":" `
A9=`less $dir/cross9/$file | cut -f3 |cut -f2 -d":" `
A10=`less $dir/cross10/$file | cut -f3 |cut -f2 -d":" `


T=`expr $E1 + $E2 + $E3 + $E4 + $E5 + $E6 + $E7 + $E8 + $E9 + $E10 + $C1 + $C2 + $C3 + $C4 + $C5 + $C6 + $C7 + $C8 + $C9 + $C10`

Acc=$(bc <<< "scale=10;$C/$T")

printf "MediaC:%d\tE:%d\tAcc:%s\n " $C $E $Acc > $dir/cross10$file
for i in `seq 1 10`
do
 less $dir/cross$i/$file >> $dir/cross10$file
done
}

function crosswekasmooptimal_es()
{
WEKA_PATH=/home/kepa/weka-3-8-3
export CLASSPATH=$CLASSPATH:/home/kepa/weka-3-8-3/weka.jar #:/usr/share/java/libsvm.jar:/usr/share/java
CP="$CLASSPATH:/usr/share/java/"
###########################################################################
##TRAINING AND TESTING  WITH OPTIMAL PARAMETERS
########################################################################
g=0.4 #large gamma leads to high bias (underfit) and low variance models, and vice-versa.Why is the default value of Gamma in Gaussian RBF kernel 1/number_of_features?large number_of_features tends to overfitting, small gamma trends to underfitting , so it’s maybe a heuristic setting to make a tradeoff.1/100=0.01
#c=1.0 #"soft margin" SVM that allows some examples to be "ignored" or placed on the wrong side of the margin; c=1000 "hard margin" edo c=0.1 "soft margin".A large C gives you low bias(overfit) and high variance. Low bias because you penalize the cost of missclasification a lot.

#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.classifiers.functions.SMO -C $c -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K "weka.classifiers.functions.supportVector.RBFKernel -C 250007 -G $g" -t $dir/cross10$modelo/cross$i/train_cab.arff -d $dir/cross10/etrain.model -x 10 -o -i -c last > $dir/cross10/cross10results.txt
#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.classifiers.functions.SMO -c $CLASE -l $dirtrain/etrain.model -T $dirtest/etest.morfo.cab.nominaltextstringtowordvector$N.arff -p 0 > $dirtest/emaitza.test.output
#weka cross 10 automatikoa parametrizatu ahal dut $c $g
#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.classifiers.functions.SMO -C $c -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K "weka.classifiers.functions.supportVector.RBFKernel -C 250007 -G $g" -t $dirtrain/etrain.morfo.cab.nominaltextstringtowordvector$N.arff -d $dirtrain/etrain.model -x 10 -o -i -c $CLASE > $dirtrain/cross10results.txt

#train default 

#test test
#java -cp $CP -Xmx1024m --add-opens=java.base/java.lang=ALL-UNNAMED weka.classifiers.functions.SMO -c $CLASE -l $dirtrain/etrain.model -T $dirtest/etest.morfo.cab.nominaltextstringtowordvector$N.arff -o -i > $dirtest/testresults.txt

}
function wekainstalatuubuntun()
{
sudo apt-get update
sudo apt-get install weka
sudo apt-get install libsvm-java
}
function weka()
{
#con weka:https://machinelearningmastery.com/how-to-run-your-first-classifier-in-weka/
#/media/datos/Dropbox/ikerkuntza/UZ/programak/logisticregression_uc
#https://datascience.stackexchange.com/questions/40900/whats-the-difference-between-sklearn-f1-score-micro-and-weighted-for-a-mult/40904#40904
WEKA_PATH=/home/kepa/weka-3-8-3
export CLASSPATH=$CLASSPATH:/home/kepa/weka-3-8-3/weka.jar #:/usr/share/java/libsvm.jar:/usr/share/java
CP="$CLASSPATH:/usr/share/java/"
cd /media/datos/Dropbox/ikerkuntza/metrix-env/sepln2020/aztertestnlpcube/dataset_aztertest_full
java -cp $CP -Xmx1024m weka.gui.explorer.Explorer
}


function fin()
{
	echo -e "¿Quieres salir del programa?(S/N)\n"
        read respuesta
	if [ $respuesta == "N" ] 
		then
			opcionmenuppal=0
		fi	
}
### Main ###
opcionmenuppal=0
modelo=stanford
while test $opcionmenuppal -ne 10
do
	#Muestra el menu
       	echo -e "1 obtenerdatossimple5en5 \n"
        echo -e "2 obtenerdatoscomplejo5en5 \n"
        echo -e "3 obtenerdatosmultiaztertest_eu stanford\n"
	echo -e "4 Crear data-cross10"
        echo -e "5 Aplicar cross10 con weka SMO default\n" #, para feature selection y seleccionar los parametros y el algoritmo \n"
        echo -e "6 Aplicar weka feature selection y seleccionar los parametros y el algoritmo \n"
	echo -e "7 generar el mejor modelo con train y guardar \n"
	echo -e "8 testear los datos de test\n"
        echo -e "9 weka \n"
        echo -e "10 Exit \n"
	read -p "Elige una opcion:" opcionmenuppal
	case $opcionmenuppal in
                       	1) obtenerdatossimple5en5;;
                        2) obtenerdatoscomplejo5en5;;
			3) obtenerdatosmultiaztertest_eu $modelo;;
			4) cross10banatu_es $modelo;;
                        5) crosswekasmodefault_es $modelo;;
			6) crosswekafs_es $modelo;;
                        7) weka;;
			8) weka;;
			10) fin;;
			*) ;;

	esac 
done 

echo "Fin del Programa" 
exit 0 

