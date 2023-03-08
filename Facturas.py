from bs4 import BeautifulSoup
import os, glob
import pandas as pd
from pathlib import Path
import csv

path = 'Downloads/FACTURAS EJEMPLO'


def parse_xml(path: str)-> dict:
    try:
        with open(os.path.join(os.getcwd(),filename),'r',encoding = 'utf-8') as f:
            file = f.read()
    except Exception as error:
        print(f"Hubo un error en el documento{filename}, se omite. {error}")
        return {
            "Razon social": "ERROR",
            "RUC del vendedor": "00000",
            "Fecha de emisión": "00000",
            "Número de autorización": "00000",
            "Número de factura": "00000",
            "Subtotal 12%": 0,
            "Subtotal 0%":  0,
            "Subtotal sin impuestos": 0,
            "IVA 12%": subtotal_12 * 0.12,
            "Total sin descuento": subtotal_12 + subtotal_0 + subtotal_sin + subtotal_12 * 0.12
        }

    soup = BeautifulSoup(file,'xml')     
    
    
    listaSoup = BeautifulSoup("<comprobante>"+soup.comprobante.contents[0]+"</comprobante>","lxml")
    
    listaImp=listaSoup.find_all("totalimpuesto")
    print(listaImp)
    
    numAut = soup.numeroAutorizacion.string
    subtotal_12 = 0
    subtotal_0 = 0
    subtotal_sin = 0

    for impuesto in listaImp:
        if impuesto.codigoporcentaje.string == "2":
            subtotal_12 = float(impuesto.baseimponible.string)
        elif impuesto.codigoporcentaje.string == "0":
            subtotal_0 = float(impuesto.baseimponible.string)
        elif impuesto.codigoporcentaje.string == "6":
            subtotal_sin = float(impuesto.baseimponible.string)
        
        
        
    return {
        "Razon social": listaSoup.razonsocial.string,
        "RUC del vendedor": listaSoup.ruc.string,
        "Fecha de emision": listaSoup.fechaemision.string,
        "Numero de factura": numAut[-25:-22]+"-"+numAut[-22:-19]+"-"+numAut[-19:-10],
        "Numero de Autorizacion": numAut,
        "Subtotal 12%": subtotal_12,
        "Subtotal 0%":  subtotal_0,
        "Subtotal sin impuestos": subtotal_sin,
        "IVA 12%": subtotal_12 * 0.12,
        "Total sin descuento": subtotal_12 + subtotal_0 + subtotal_sin + subtotal_12 * 0.12
    }

def export(scrapped: list) -> None:
    csv_file = "CuadroImpuestos.xlsx"

    # with open(csv_file,'w') as csvfile:
    #     writer = csv.DictWriter(csvfile,fieldnames= scrapped[0].keys())
    #     writer.writeheader()
    #     writer.writerows(scrapped)
    df = pd.DataFrame(scrapped)
    
    df["RUC del vendedor"] = df["RUC del vendedor"].map("{}".format)
    df["Numero de Autorizacion"] = df["Numero de Autorizacion"].map("{}".format)
    df["IVA 12%"] = df["IVA 12%"].map("{:.2f}".format)
    df["Total sin descuento"] = df["Total sin descuento"].map("{:.2f}".format)

    convert_dict = { 
        "RUC del vendedor": str,
        "Numero de Autorizacion": str
    }
    df = df.astype(convert_dict)
    
    filepath = Path(path+"/"+csv_file)
    filepath.parent.mkdir(parents = True, exist_ok = True)
    df.to_csv(filepath, index = False)
    # writer = pd.ExcelWriter(path+"/"+csv_file,mode= "A")
    # df.to_excel(writer, sheet_name= "Cuadro")
    # writer.save()
    # with pd.ExcelWriter(path+"/"+csv_file, engine="openpyxl", if_sheet_exists="new",mode="a") as writer:
    #     df.to_excel(writer, sheet_name="name", startrow=0, startcol=0)




if __name__ == "__main__":
    
    content=[]
    for filename in glob.glob(os.path.join(path,'*.xml')):
        print( "\n----------", filename.split('\\')[1],"-----\n")
        print(filename)
        scrapped = parse_xml(path)
        content.append(scrapped)
    
    for dic in content:
        print(dic)
    
    export(content)