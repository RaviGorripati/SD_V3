import numpy as np
import xlrd
import csv
import matplotlib.pyplot as plt
#import gmplot


# initialize depth (in feet) of water table
water_depth=20
WDA=[]	#water depth array
YIELD_PER_WELL = 1            # mm
YIELD_INC=0.20	#Yield increment % by year
VILLAGE_AREA = (2000*4000)	#2km * 4km
WORKING_DAYS=270    # well working days 9 months per year

START_YEAR = 1960
END_YEAR = 2010
NUM_SEASONS = 1
MM_TO_FEET = (0.1 / (2.54*12))
PERCOLATION = .10
PER_INC=0.01
POROSITY=1
FERTILIZERS=1975
TUBE_WELLS_TECH=1980
AVG_DEPTH=56# open well avg water depth
TUBE_WELLS=[]
TOTAL_WELLS=76 #Initial well count
SF=1    #soil fertility 100 %
SOIL_DEP=0.02 #Soil depletion 2%
FEW=3   #farming extent under well in acres
YA=25.0 # yield in bags of rice per acre
PRICE=1 # price unit per rice bag etc,
FP=5    # % of farming area increment every year(%)
INCOME=0.5 # Farm income percentage(50%) after all expendatures
EXD=0.30    #Over exploitation due to disel engines(10%)
EXP=1.0	#Over exploitation due to pipeline(15%)
EXEM=1.5   #Over exploitation due to Elecric motors(20%)
EXFE=2.5   #Over exploitation due to free electricity(30%)
MAX_WATER_DEPTH=900 # If max water depth crossed stoped tube wells digging

WWC=[]	#working wells count
Y=[]	#store year index
FE=1	#Farming extent
CY=1	#crop yield
FI=1	#farm income
FIA=[]
SFA=[]  #soil fertility array
ww_data_list=[] # collected data lists
c_data_years=[]
c_data_wells=[]

#Yield increase % due to fertilizers(20 - 30%)


# read year+season-wise rainfall data
bk_rainfall=xlrd.open_workbook("rainfall.xls")
sh_rainfall = bk_rainfall.sheet_by_index(0)

# read well data: location(x, y), depth
bk_wells=xlrd.open_workbook("well_data.xls")
sh_wells=bk_wells.sheet_by_index(0)

# set up map interface
# e.g. using MatPlotLib:
#       each cell = 1 acre; total area = 100x100 acres


with open('./ww_count.csv') as wells_data:  # working wells data 5 years span wise
    well_reader=csv.DictReader(wells_data)
    for row in well_reader:
        ww_data_list.append([row['year'],row['ww_count']])

for r in ww_data_list:
    c_data_years.append(int(r[0]))
    c_data_wells.append(int(r[1]))

# simulate year+season-wise
for year in range(START_YEAR, (END_YEAR+1), 1):
	for season in range(0,NUM_SEASONS,1):	#season wise

		ww=0
		print(year)  
		print (water_depth)
		cell_no=sh_rainfall.cell((year-START_YEAR), (season+1))
        rainfall=cell_no.value
        water_depth = water_depth - (rainfall*PERCOLATION+(PERCOLATION*PER_INC) / POROSITY) 	# recharge due to rainfall
        WDA.append(water_depth)
        if water_depth < 0:
            water_depth=3
        print ("water depth",water_depth)

        
        working_wells = []
        dry_wells = []
       

        if year >= TUBE_WELLS_TECH and water_depth < MAX_WATER_DEPTH:			# Tube wells installation
        	if water_depth >= AVG_DEPTH:
        		for n in range(int(TOTAL_WELLS*0.25)):	#10% tube wells increased every year if water depth > 50 feet1
        			if year >= (TUBE_WELLS_TECH+10):
        				well_depth=np.random.randint(400,800) #tube well depth between 500 to 1000
        			else:
        				well_depth=np.random.randint(300,400)	#tube well depth between 300 to 500
        			TUBE_WELLS.append(well_depth)
        	else:										# other wise only 5% wells increased every year
        		for n in range(int(TOTAL_WELLS*0.20)):
        			if year >= (TUBE_WELLS_TECH+10):
        				well_depth=np.random.randint(400,800)
        			else:
        				well_depth=np.random.randint(300,400)
        			TUBE_WELLS.append(well_depth)

        print("tube wells:", len(TUBE_WELLS))

        for well in range(sh_wells.nrows): 	# find working wells and not working wells
            depth=sh_wells.cell(well,2)
            x=sh_wells.cell(well,3)
            y=sh_wells.cell(well,4)
            
            if depth.value - water_depth >= 5:     #working well must contain min 10 feet water
                working_wells.append([x.value,y.value])
            else:
                dry_wells.append([x.value,y.value])

        print("w open wells",len(working_wells))
		
        for tw in range(len(TUBE_WELLS)):	# check tube wells
			if TUBE_WELLS[tw] - water_depth >= 10:
				working_wells.append([tw,20])
			else:
				dry_wells.append([tw,20])
        #print(working_wells)
        working_well=np.asarray(working_wells)
        dry_well=np.asarray(dry_wells)
        ww=len(working_wells)
        print("ww",ww)
		

        if year >= FERTILIZERS and ww >=(TOTAL_WELLS*0.3):	#fertility utilization factor will be calculated when working wells > 30%
			SF=SF-(SF*SOIL_DEP)# Redusing SF by %
			#print(SF)
		

        if year >= FERTILIZERS and year <= FERTILIZERS+4: 	
			ya=YA+((YA/100)*np.random.randint(20,30))		# incrementing yield initial stage of fertilizers introduction
			print(ya)
			
        else:
			ya=YA	
        FE=ww*FEW
        FE=FE+(FE/100)*np.random.randint(0,5)	#Farming increased every year by FP
        CY=FE*ya



        if year < FERTILIZERS or year >= (FERTILIZERS+4):	#calculating Farm Income(FI)
			F=(CY*PRICE)*SF
			FI=F-(F*INCOME)
        else:
			F=CY*PRICE
			FI=F-(F*INCOME)
		
        print(FI)

        

        #print("FI",FI)
        FIA.append(FI)
        WWC.append(ww)
        SFA.append(SF)
        Y.append(year)
        wd = len(working_wells)*YIELD_PER_WELL+(YIELD_PER_WELL*YIELD_INC)
        water_depth = water_depth + wd
        """if year < 1970 and len(working_wells)>0:			#calculating discharge of ground water
			water_depth = water_depth + wd
            #water_depth = water_depth + (len(working_wells)*YIELD_PER_WELL / (VILLAGE_AREA*POROSITY))
        elif year >= 1970 and year < 1980 and len(working_wells)>0:	
			water_depth = water_depth + wd + (wd*EXD)
            #water_depth = water_depth + (len(working_wells)*YIELD_PER_WELL / (VILLAGE_AREA*POROSITY)) + (water_depth*EXD) # 2% more utilization due to disel engines tech
        elif year >= 1980 and year < 1985 and len(working_wells)>0:
        	water_depth = water_depth + wd + (wd*EXP)
        	##water_depth = (water_depth + ((len(working_wells)*YIELD_PER_WELL*WORKING_DAYS*MM_TO_FEET*PERCOLATION)/POROSITY)) + (water_depth*EXEM)
            #water_depth = water_depth + (len(working_wells)*YIELD_PER_WELL / (VILLAGE_AREA*POROSITY)) + (water_depth*EXEM) # 10% more utilization due to disel engines tech
        elif year >= 1985 and year < 2003 and len(working_wells)>0:
        	water_depth = water_depth + wd + (wd*EXEM)
        elif year >= 2004 and len(working_wells)>0:
        	water_depth = water_depth + wd + (wd*EXFE)
        	#water_depth = (water_depth + ((len(working_wells)*YIELD_PER_WELL*WORKING_DAYS*MM_TO_FEET*PERCOLATION)/POROSITY))+(water_depth*EXFE)
            #water_depth = water_depth + (len(working_wells)*YIELD_PER_WELL / (VILLAGE_AREA*POROSITY)) + (water_depth*EXFE) # 30% more utilization due to disel engines tech
		"""	

        print (water_depth)
        #print("total no wells",TOTAL_WELLS+len(TUBE_WELLS))
		#print()
wwc=np.array(WWC)
c_data_year=np.array(c_data_years)
c_data_well=np.array(c_data_wells)
#print(FIA)
#print(SFA)
print(WDA)
f1 = plt.figure("Working Wells")
plt.axis([1960, 2010,0,200])
plt.xlabel("years")
plt.ylabel("Working Wells")
#plt.plot(c_data_year,wwc, label='Simulation')
#plt.plot(c_data_year,c_data_well, label='Collected' )
plt.plot(Y,WWC,label='Simulation')
#plt.plot(Y,c_data_well,label='Collected')
plt.legend()
plt.savefig("Working wells")
f1.show()


f2 = plt.figure("Farm Income")
plt.axis([1960, 2010,0,5000])
plt.xlabel("Time(years)")
plt.ylabel("Income")
plt.plot(Y,FIA)
plt.savefig("Farm_Income")
f2.show()


f3 = plt.figure("Soil Fertility")
plt.axis([1960, 2010,0,1])
plt.xlabel("Time(years)")
plt.ylabel("Fertility")
plt.plot(Y,SFA)
plt.savefig("Soil_Fertility")
f3.show()

f4 = plt.figure("Water Depth")
plt.axis([1960, 2010,1000,0])
plt.xlabel("Time(years)")
plt.ylabel("Water Depth")
plt.plot(Y,WDA)
plt.savefig("water_depth")
f4.show()

raw_input()



