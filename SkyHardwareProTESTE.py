from tabulate import tabulate
import numpy as np
import pandas as pd
import codecs
import urllib
import webbrowser

#Funcoes
def readcsvAndSelect():
    #Essa funcao le os arquivos csv necessarios

    #Motores E Helicess

    df_mp = pd.read_csv('motoresEpropellers.csv')
    #print(df_mp.head())
    mp_data = df_mp.iloc[:,[0,5,6,7,10,11,12,13,14,15]].values
    # 0-Conjunto-0/5-PesoMotor-1/6-n_cell-2/7-propDiam-3/10-imin-4/11-imax-5/12-Empmin-6/13-Empmax-7/14-coef_ang-8/15-coef_lin-9
    #print(mp_data)
    mp_geral = df_mp.iloc[:,:].values

    #Baterias

    df_bat = pd.read_csv('BateriasLipoGrafenoCelulas34.csv')
    #print(df_bat.head())
    bat_data = df_bat.iloc[:,[0,2,3,4,5,9]].values
    # 0-Numeracao-0/2-TipoBat(0->lipo,1->graf)-1/3-mAh-2/4-Ncell-3/5-Crating-4/9-peso-5
    #print(bat_data)
    bat_geral = df_bat.iloc[:,:].values

    return mp_data , bat_data , mp_geral , bat_geral


def TEmedmax():
    #Essa funcao calcula a o percentual do empuxo máximo usado num voo padrão em média

    #Drone Padrão
    E_max = 850*4
    i_med_log = 10.179451722343641
    a = 138
    b = 0
    E_med_log = a*i_med_log + b
    TEmedmax = E_med_log/E_max
    return TEmedmax


def dados_usuario():
    # Essa funcao coleta os dados que o projetista deve fornecer
    print()
    print("===================================================")
    print("============= SKY HARDWARE PRO v1.0 ===============")
    print("===================================================")
    print()
    Pframe = float(input("Peso do frame e componentes eletrônicos (exceto Motor,Helice e Bateira) em gramas : "))
    def Tep():
        print("Defina a aplicação que deseja :")
        opcao = int(input("1) Drone para Filmagens \n 2)Drone com vôo Estável de propósito geral \n 3)Drone de acrobacia \n 4) Personalizar Drone"))
        if opcao == 1:
            Tep = 4
        elif opcao == 2:
            Tep = 4
        elif opcao == 3:
            Tep = 10
        else:
            Tep = float(input("Ensira o Thrust to weight ratio (Taxa empuxo peso) desejada :"))
        print("A taxa empuxo peso para seu drone será = ", Tep)
        return Tep

    tmax_voo_min = float(input("Tempo máximo de voo desejado em minutos (Número Inteiro) : "))
    prop_diam_max =float(input("Tamanho maximo do diâmetro do propeller em polegadas : "))
    Tep = Tep()
    return Pframe,tmax_voo_min,prop_diam_max,Tep

   
def ordena_lista_pelo_tempo(lista_final):
    ind=np.argsort(lista_final[:,-1])
    lista_ordenada =lista_final[ind]
    return lista_ordenada

def resultados(i_MH,j_Bat, mp_geral , bat_geral):
    #Essa funcao devolve uma lista dos parâmetros de interesse referentes a bateria, helice e motor para mostrar ao usuário final
    #Motores: Tipo , Nome_motor , Marca, kv ,n_celuas , peso
    motorSel  = [mp_geral[i_MH][1],mp_geral[i_MH][2],mp_geral[i_MH][3],mp_geral[i_MH][4],mp_geral[i_MH][6],mp_geral[i_MH][5]]

    def propeller(i_MH,mp_geral):
        #Essa funcao retorna o nome do propeller
        #Diametro da helice
        if mp_geral[i_MH][7] < 10:
           prop_diam = str(int(mp_geral[i_MH][7]*10))
        else:
           prop_diam = str(int(mp_geral[i_MH][7]))
        prop_diam = prop_diam[0] + prop_diam[1]
        #Pitch da helice
        if int(mp_geral[i_MH][8][0]) < 10:
           prop_pitch = str(int(mp_geral[i_MH][8][0])*10)
        else:
           prop_pitch = str(int(mp_geral[i_MH][8][0]))
        prop_pitch = prop_pitch[0] + prop_pitch[1]

        prop_name = prop_diam + prop_pitch
        return prop_name

    propSel = [propeller(i_MH,mp_geral)]
    
    def type_bat(j_Bat,bat_geral):

        if bat_geral[j_Bat][2] == 0:
            tipo = 'Lipo'
        else:
            tipo = 'Grafeno'

        return tipo


    #Bateria: Marca,Lipo/grafeno,mAh,n_celulas,C,Peso
    batSel = [bat_geral[j_Bat][1] , type_bat(j_Bat,bat_geral) , bat_geral[j_Bat][3] , bat_geral[j_Bat][4] , bat_geral[j_Bat][5] , bat_geral[j_Bat][6]]

    resultado = [motorSel[0],motorSel[1],motorSel[2],motorSel[3],motorSel[4],motorSel[5],propSel[0],batSel[0],batSel[1],batSel[2],batSel[3],batSel[4],batSel[5]]
    return resultado

def Tempo_de_voo():
    #Constantes
    Phelicepadrao = 12

    #Dados do Usuário
    Pframe,tmax_voo_min,prop_diam_max,Tep = dados_usuario()

    #Dados arquivos CSV
    mp_data , bat_data , mp_geral , bat_geral = readcsvAndSelect()

    #Contas
    list_bat_mot_prop = []
    for i in range(len(mp_data)):
        for j in range(len(bat_data)):
            if int(mp_data[i][2]) == int(bat_data[j][3]): #Se o numero de celulas da bateria for compatível com aquele motor
                if mp_data[i][3] <= prop_diam_max : #Se o prop_diam <= prop_diam_maximo
                    Pdrone = Pframe + 4*(mp_data[i][1]+Phelicepadrao) + bat_data[j][5] 
                    E_maxN = Pdrone*Tep
                    if E_maxN <= 4*mp_data[i][7] : #Se o empuxo maximo calculado for menor do que aquele que so 4 motores podm fornecer
                        E_medN = TEmedmax()*E_maxN

                        i_medN = (1/mp_data[i][8])*E_medN - (mp_data[i][9]/mp_data[i][8])
                        #O calculo da corrnete maxima da bateria esta certo
                        if (i_medN/4 <= mp_data[i][5]) and (i_medN <= bat_data[j][2]*bat_data[j][4]/1000) : 
                            #Se a corrente media for menor que a maxima corrente que o motor fornece e que a bateria fornece
                            # i_max_bateria = mAh*C/1000
                            T_voo = ((bat_data[j][2]/1000)/i_medN)*60 #tempo de voo em (60min/1h)*(mAh/1000)/A [minutos]
                            #Lista com o conjunto a ser comprado e autonomia associada [(num_motor&prop),num_bateria,Tempo_de_voo]
                            r = resultados(int(mp_data[i][0])-1,int(bat_data[j][0])-1, mp_geral , bat_geral)

                            list_bat_mot_prop.append([r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12],T_voo]) 
    lista_final = np.array(list_bat_mot_prop)
    lista_fina_ordenada = ordena_lista_pelo_tempo(lista_final)

    df = pd.DataFrame(data=lista_fina_ordenada, columns=["MotorType","MotorName","Company","KV","N_cells","MotorWeight","Propeller","BatteryCompany","BatteryType","Charge[mAh]","N_cells","C","BatteryWeight","Autonomy[min]"])
    with pd.option_context('display.max_rows', None, 'display.max_columns', None): 
        pd.options.display.width=None # more options can be specified also
        pdtabulate=lambda df:tabulate(df,headers='keys',tablefmt='psql')
        #print(pdtabulate(df))

        #render dataframe as html
        html = df.to_html()

        #write html to file
        text_file = open("SkyHardwarePro_results.html", "w")
        text_file.write(html)
       

        #file = codecs.open("SkyHardwarePro_results.html", "r", "utf-8")
        #print(file.read())

        #page =  urllib.urlopen('SkyHardwarePro_results.html').read()
        #print(page)
        url = 'file:///home/zolubas/Desktop/propulsao/SkyHardwarePro_results.html'
        webbrowser.open(url, new=2)

        text_file.close()

#Chamando as funções
Tempo_de_voo()

