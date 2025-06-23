
# Makefile

# Source and destination directories
SRC_DIR := ./deployment_templates
# TPL_DIR:='./deployment.dev'


DEST_DEV_DIR := ./deployment.dev
DEST_UAT_DIR := ./deployment.uat
DEST_PROD_DIR := ./deployment.prod

# Find all directories with .dev suffix
FIND_DEV_DIRS := $(shell find ${SRC_DIR} -maxdepth 1 -type d -name '*.dev' -not -path ${DEST_DEV_DIR})

FIND_UAT_DIRS = $(shell find ${SRC_DIR} -maxdepth 1 -type d -name '*.uat' -not -path ${DEST_UAT_DIR})
FIND_PROD_DIRS = $(shell find ${SRC_DIR} -maxdepth 1 -type d -name '*.prod' -not -path ${DEST_PROD_DIR})

# Find all directories with no .
BASE_DIRS := $(shell find $(SRC_DIR) -maxdepth 1 -type d -not -name '*.*' -not -path $(SRC_DIR))

# Find all files in .dev with .tpl suffix
DEV_TPL_FILES = $(shell find ${DEST_DEV_DIR} -maxdepth 3 -type f -name '*.tpl' )
UAT_TPL_FILES = $(shell find ${DEST_UAT_DIR} -maxdepth 3 -type f -name '*.tpl' )
PROD_TPL_FILES= $(shell find ${DEST_PROD_DIR} -maxdepth 3 -type f -name '*.tpl' )

# Find all files in .dev with .tpl suffix
# DEV_TPL_FILES := $(shell find $(DEST_DEV_DIR) -maxdepth 3 -type f -name '*.tpl' )
# SET_TPL_DEV_DIR=$(eval TPL_DIR=$(DEST_DEV_DIR))
# Default target
# all: copy-dirs


MERGE_FILE2=''
FINAL_MERGE_FILE2=${MERGE_FILE2}

replace-dev-tpl-vars: MERGE_FILE2=./master_config/dev.master.csv
replace-uat-tpl-vars: MERGE_FILE2=./master_config/uat.master.csv
replace-prod-tpl-vars: MERGE_FILE2=./master_config/prod.master.csv


merge-csv:
#	Extract headers
#	@echo $(FINAL_MERGE_FILE2)
	@head -n 1 ./master_config/base.master.csv > header1.txt
	@head -n 1 $(FINAL_MERGE_FILE2) > header2.txt
#	Remove headers for joining
	@tail -n +2 ./master_config/base.master.csv > file1_noheader.csv
	@tail -n +2 $(FINAL_MERGE_FILE2) > file2_noheader.csv
#	Sort the no-header files
	@sort -t ',' -k 1,1 file1_noheader.csv > file1_noheader_sorted.csv
	@sort -t ',' -k 1,1 file2_noheader.csv > file2_noheader_sorted.csv
#	Perform the join
#	@join -t ',' -1 1 -2 1 file1_noheader_sorted.csv file2_noheader_sorted.csv > joined_data.csv
	@join -t, -a1 -a2 file2_noheader_sorted.csv file1_noheader_sorted.csv | cut  -d, -f 1,2 > joined_data.csv
	@cat header1.txt > final_merged.csv
	@cat joined_data.csv >> final_merged.csv
	@rm header1.txt header2.txt file1_noheader.csv file2_noheader.csv file1_noheader_sorted.csv file2_noheader_sorted.csv joined_data.csv
#	rm 	final_merged.csv


clean-dev:
	@rm -rf deployment.dev

# Rule to copy no '.' dirs and then '.dev' dir files into base dir
copy-dev-dirs: clean-dev
	@mkdir -p $(DEST_DEV_DIR)
	cp $(SRC_DIR)/* $(DEST_DEV_DIR) &2>/dev/null
	@for dir in $(BASE_DIRS); do \
		echo "Copying $$dir to $(DEST_DEV_DIR)"; \
		cp -r "$$dir" $(DEST_DEV_DIR); \
	done
	@for dir in $(FIND_DEV_DIRS); do \
		new_name=$$(echo "$$dir" | sed -n 's/^\(.*\/\)*\(.*\)/\2/p' | sed "s/.dev//g"); \
		echo "Copying $$dir to $(DEST_DEV_DIR)/$$new_name"; \
		cp -r "$$dir"/* $(DEST_DEV_DIR)/$$new_name; \
	done

# $(SET_TPL_DEV_DIR)
# echo $(TPL_DIR)

replace-dev-tpl-vars: merge-csv
	@echo 'Begin replace-tpl-vars'
	@for fil in $(DEV_TPL_FILES); do \
		new_name=$$(echo "$$fil" | sed "s/.tpl//g"); \
		echo "Altering $$fil to $$new_name"; \
		awk -F, 'NR==FNR{a[$$1]=$$2; next} {for (i in a) gsub(i,a[i]); print}' final_merged.csv $$fil > $$new_name; \
		echo "Deleting $$fil"; \
		rm "$$fil"; \
	done
	@echo 'End replace-tpl-vars'
#	cat final_merged.csv
	@rm 	final_merged.csv

# .PHONY: all copy-dirs






clean-uat:
	@rm -rf deployment.uat

copy-uat-dirs: clean-uat
	@mkdir -p $(DEST_UAT_DIR)
	cp $(SRC_DIR)/* $(DEST_UAT_DIR) &2>/dev/null
	@for dir in $(BASE_DIRS); do \
		echo "Copying $$dir to $(DEST_UAT_DIR)"; \
		cp -r "$$dir" $(DEST_UAT_DIR); \
	done
	@for dir in $(FIND_UAT_DIRS); do \
		new_name=$$(echo "$$dir" | sed -n 's/^\(.*\/\)*\(.*\)/\2/p' | sed "s/.uat//g"); \
		echo "Copying $$dir to $(DEST_UAT_DIR)/$$new_name"; \
		cp -r "$$dir"/* $(DEST_UAT_DIR)/$$new_name; \
	done

replace-uat-tpl-vars: merge-csv
	@echo 'Begin replace-tpl-vars'
	@for fil in $(UAT_TPL_FILES); do \
		new_name=$$(echo "$$fil" | sed "s/.tpl//g"); \
		echo "Altering $$fil to $$new_name"; \
		awk -F, 'NR==FNR{a[$$1]=$$2; next} {for (i in a) gsub(i,a[i]); print}' final_merged.csv $$fil > $$new_name; \
		echo "Deleting $$fil"; \
		rm "$$fil"; \
	done
	@echo 'End replace-tpl-vars'
	rm 	final_merged.csv

clean-prod:
	@rm -rf deployment.prod

copy-prod-dirs:
	@mkdir -p $(DEST_PROD_DIR)
	@cp $(SRC_DIR)/* $(DEST_PROD_DIR) &2>/dev/null
	@for dir in $(BASE_DIRS); do \
		echo "Copying $$dir to $(DEST_PROD_DIR)"; \
		cp -r "$$dir" $(DEST_PROD_DIR); \
	done
	@for dir in $(FIND_PROD_DIRS); do \
		new_name=$$(echo "$$dir" | sed -n 's/^\(.*\/\)*\(.*\)/\2/p' | sed "s/.prod//g"); \
		echo "Copying $$dir to $(DEST_PROD_DIR)/$$new_name"; \
		cp -r "$$dir"/* $(DEST_PROD_DIR)/$$new_name; \
	done

replace-prod-tpl-vars: merge-csv
	@echo 'Begin replace-tpl-vars'
	@for fil in $(PROD_TPL_FILES); do \
		new_name=$$(echo "$$fil" | sed "s/.tpl//g"); \
		echo "Altering $$fil to $$new_name"; \
		awk -F, 'NR==FNR{a[$$1]=$$2; next} {for (i in a) gsub(i,a[i]); print}' final_merged.csv $$fil > $$new_name; \
		echo "Deleting $$fil"; \
		rm "$$fil"; \
	done
	@echo 'End replace-tpl-vars'
#	cat final_merged.csv
	@rm final_merged.csv


create-dev: copy-dev-dirs replace-dev-tpl-vars
	@echo 'Done'

create-uat: copy-uat-dirs replace-uat-tpl-vars
	@echo 'Done'


create-prod: copy-prod-dirs replace-prod-tpl-vars
	@echo 'Done'





