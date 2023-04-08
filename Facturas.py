from bs4 import BeautifulSoup
import os, glob
import pandas as pd
from pathlib import Path
import traceback

path = 'Downloads/FACTURAS'


def parse_xml(path: str)-> dict:
    try:
        with open(os.path.join(os.getcwd(),filename),'r',encoding = 'utf-8') as f:
            file = f.read()
            soup = BeautifulSoup(file,'xml')
            if soup.comprobante is None:
                listaSoup = soup  
                listaImp = listaSoup.find_all("totalImpuesto")
                numAut = listaSoup.find('claveAcceso').string
                razSoc = listaSoup.find('razonSocial').string
                numRuc = listaSoup.find('ruc').string
                fecEmi = listaSoup.find('fechaEmision').string
                tipoFact = 2
                
            else:
                info = soup.comprobante.contents
                listaSoup = BeautifulSoup("<comprobante>"+info[0]+"</comprobante>","lxml")
                listaImp=listaSoup.find_all("totalimpuesto")
                numAut = soup.numeroAutorizacion.string
                razSoc = listaSoup.razonsocial.string
                numRuc = listaSoup.ruc.string
                fecEmi = listaSoup.fechaemision.string
                tipoFact = 1
                             
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

    subtotal_12 = 0
    subtotal_0 = 0
    subtotal_sin = 0

    for impuesto in listaImp:
        if tipoFact == 1:
            codPor = impuesto.codigoporcentaje
            baseImp = impuesto.baseimponible
        elif tipoFact == 2:
            codPor = impuesto.codigoPorcentaje
            baseImp = impuesto.baseImponible
            
        if codPor.string == "2":
            subtotal_12 = float(baseImp.string)
        elif codPor.string == "0":
            subtotal_0 = float(baseImp.string)
        elif codPor.string == "6":
            subtotal_sin = float(baseImp.string)
         
    return {
        "Razon social": razSoc,
        "RUC del vendedor": numRuc,
        "Fecha de emision": fecEmi,
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
    df.to_excel(filepath, index = False)



if __name__ == "__main__":
    
    content=[]
    for filename in glob.glob(os.path.join(path,'*.xml')):
        print( "\n----------", filename.split(os.sep)[1],"-----\n")
        print(filename)
        try:
            scrapped = parse_xml(path)
            content.append(scrapped)
        except Exception as error:
            print("Hubo un problema con la factura "+ filename.split(os.sep)[1])
            print(error)
            traceback.print_exc()
    
    for dic in content:
        print(dic)
    
    export(content)