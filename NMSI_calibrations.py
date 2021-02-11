import pandas as pd

UMV_df = pd.read_csv('DDM_UMV3.csv')
MRC_df = pd.read_csv('DDM_MRC3.csv')
FOI_df = pd.read_csv('DDM_FoI3.csv')
LDC_df = pd.read_csv('DDM_LDC3.csv')


def check_stat_class(x):
    if 'statistics' in str(x).lower():
        return 1
    else:
        return 0


UMV_df['statistics'] = UMV_df['Class'].apply(lambda x: check_stat_class(x))
MRC_df['statistics'] = MRC_df['Class'].apply(lambda x: check_stat_class(x))
FOI_df['statistics'] = FOI_df['Class'].apply(lambda x: check_stat_class(x))
LDC_df['statistics'] = LDC_df['Class'].apply(lambda x: check_stat_class(x))


UMV_df = UMV_df[UMV_df['statistics'] == 1]
MRC_df = MRC_df[MRC_df['statistics'] == 1]
FOI_df = FOI_df[FOI_df['statistics'] == 1]
LDC_df = LDC_df[LDC_df['statistics'] == 1]


UMV_items_list = list(UMV_df)
MRC_items_list = list(MRC_df)
FOI_items_list = list(FOI_df)
LDC_items_list = list(LDC_df)

all_items_list = UMV_items_list[3:] + MRC_items_list[3:] + FOI_items_list[3:] + LDC_items_list[3:]
OE_items = [x for x in all_items_list if 'OE' in x]  # we don't want to consider OE items
non_items = [x for x in all_items_list if 'S110' in x]  # unnecessary items unique to DDM

UMV_df.drop(columns={'Respondent Id', 'Class', 'statistics'}, inplace=True)  # we want to use Assign ID instead
MRC_df.drop(columns={'Respondent Id', 'Class', 'statistics'}, inplace=True)
FOI_df.drop(columns={'Respondent Id', 'Class', 'statistics'}, inplace=True)
LDC_df.drop(columns={'Respondent Id', 'Class', 'statistics'}, inplace=True)

# create one whole dataset with all constructs
new_df = pd.merge(UMV_df, MRC_df, how='outer', on=['Assignment Id', 'Activities'])
new_df = pd.merge(new_df, FOI_df, how='outer', on=['Assignment Id', 'Activities'])
new_df = pd.merge(new_df, LDC_df, how='outer', on=['Assignment Id', 'Activities'])

new_df = new_df.drop(OE_items, axis=1)
new_df = new_df.drop(non_items, axis=1)

activity_list = [x for x in new_df['Activities'].unique()]

assign_id_list = []
for item in activity_list:
    df = new_df[new_df['Activities'] == item]
    df = df.applymap(lambda x: str(x).replace('-', 'NA').replace('---', 'NA').replace('Blank', 'NA').replace(r'^\s+$', 'NA').replace('NANANA', 'NA'))
    df['count_empty'] = df.eq('NA').sum(axis=1)
    num_ques = (len(list(df))-3) - df['count_empty'].min()
    min_answered = int(num_ques*.2)  # 20% rounded down to the nearest whole number
    missing_ids_list = [x for x in df['Assignment Id'][df['count_empty'] > (len(list(df))-3) - min_answered]]
    assign_id_list = assign_id_list + missing_ids_list

UMV_df2 = UMV_df[~UMV_df['Assignment Id'].isin(assign_id_list)]
MRC_df2 = MRC_df[~MRC_df['Assignment Id'].isin(assign_id_list)]
FOI_df2 = FOI_df[~FOI_df['Assignment Id'].isin(assign_id_list)]
LDC_df2 = LDC_df[~LDC_df['Assignment Id'].isin(assign_id_list)]

###########################################################################################################################################
# UMV specific processing
R_UMV_df = UMV_df2.drop(columns={'Assignment Id', 'Activities', 'CuppaJoe.02_OE', 'MMpacket.04ab_OE', 'MMpacket.03ab_OE'})
R_UMV_df = R_UMV_df.applymap(lambda x: str(x).replace('UMV', '').replace('E', '').replace('Q', '').replace('-', 'NA').replace('Blank', 'NA').replace('e', '').replace('NANANA', 'NA').replace('q', '').replace(r'^\s+$', 'NA'))
R_UMV_df = R_UMV_df.fillna('NA')
R_UMV_df.to_csv('R_UMV.csv', index=False)

#############################################################################################################################################
# LDC specific processing DrugTrial.6b_OE
R_LDC_df = LDC_df2.drop(columns={'Assignment Id', 'Activities', 'DrugTrial.6b_OE'})
R_LDC_df = R_LDC_df.applymap(lambda x: str(x).replace('LDC', '').replace('.No', '').replace('-', 'NA').replace('Blank', 'NA').replace(r'^\s+$', 'NA'))
R_LDC_df = R_LDC_df.fillna('NA')
R_LDC_df.to_csv('R_LDC.csv', index=False)