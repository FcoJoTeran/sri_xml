import glob
import os
import traceback
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

path= "C:/Users/LENOVO/Downloads/ret-carlos2"


def parse_xml_invoice(path: str) -> dict:
    try:
        with open(os.path.join(os.getcwd(), filename), "r", encoding="utf-8") as f:
            file = f.read()
            soup = BeautifulSoup(file, "xml")
            if soup.comprobante is None:
                listaSoup = soup
                listaImp = listaSoup.find_all("totalImpuesto")
                numAut = listaSoup.find("claveAcceso").string
                razSoc = listaSoup.find("razonSocial").string
                numRuc = listaSoup.find("ruc").string
                fecEmi = listaSoup.find("fechaEmision").string
                tipoFact = 2

            else:
                info = soup.comprobante.contents
                listaSoup = BeautifulSoup(
                    "<comprobante>" + info[0] + "</comprobante>", "lxml"
                )
                listaImp = listaSoup.find_all("totalimpuesto")
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
            "Subtotal 0%": 0,
            "Subtotal sin impuestos": 0,
            "IVA 12%": 0,
            "Total sin descuento": 0
        }

    subtotal_12 = 0
    subtotal_0 = 0
    subtotal_sin = 0
    porc_iva = 0

    for impuesto in listaImp:
        if tipoFact == 1:
            codPor = impuesto.codigoporcentaje
            baseImp = impuesto.baseimponible
        elif tipoFact == 2:
            codPor = impuesto.codigoPorcentaje
            baseImp = impuesto.baseImponible
        
        #Por el iva 15%
        if codPor.string == "4":
            subtotal_12 = float(baseImp.string)
            porc_iva = 0.15
        #Por el iva 12%
        if codPor.string == "2":
            subtotal_12 = float(baseImp.string)
            porc_iva = 0.12
        elif codPor.string == "0":
            subtotal_0 = float(baseImp.string)
        elif codPor.string == "6":
            subtotal_sin = float(baseImp.string)

    return {
        "Razon social": razSoc,
        "RUC del vendedor": numRuc,
        "Fecha de emision": fecEmi,
        "Numero de factura": numAut[-25:-22]
        + "-"
        + numAut[-22:-19]
        + "-"
        + numAut[-19:-10],
        "Numero de Autorizacion": numAut,
        "Subtotal 12%": subtotal_12,
        "Subtotal 0%": subtotal_0,
        "Subtotal sin impuestos": subtotal_sin,
        "IVA 12%": subtotal_12 * porc_iva,
        "Total sin descuento": subtotal_12
        + subtotal_0
        + subtotal_sin
        + subtotal_12 * 0.12,
    }

def parse_xml_receipt(path: str) -> list:
    retenciones = []
    try:
        with open(os.path.join(os.getcwd(),filename), "r",encoding="utf-8") as f:
            file = f.read()
            soup = BeautifulSoup(file, "xml")
            info = soup.comprobante.contents
            listaSoup = BeautifulSoup(
                "<comprobante>" + info[0] + "</comprobante>", "lxml"
            )
            listaImp = listaSoup.find_all("impuesto")
            if listaImp == []:
                listaImp = listaSoup.find_all("retencion")
            numAut = soup.numeroAutorizacion.string
            razSoc = listaSoup.razonsocial.string
            numRuc = listaSoup.ruc.string
            fecEmi = listaSoup.fechaemision.string
            numDoc = listaSoup.find("numdocsustento").string
            numFac = numDoc[:3] + "-" + numDoc[3:6] + "-" + numDoc[6:15]
            fechaDoc = listaSoup.find("fechaemisiondocsustento").string
            perFis = listaSoup.find("periodofiscal").string
            print("-----Informacion del Documento-----")
            print(f"""
            Numero de Autorizacion: {numAut}
            Razon Social: {razSoc}
            RUC: {numRuc}
            Fecha de Emision: {fecEmi}
            Numero de Documento: {numFac}
            Fecha de Documento: {fechaDoc}
            Periodo Fiscal: {perFis}
                """)
            for impuesto in listaImp:
                if impuesto.codigo.string == "1":
                    tipo_impuesto = "RENTA"  
                elif impuesto.find("codigo").string == "2":
                    tipo_impuesto = "IVA"
                retenciones.append({
                    "Numero de Autorizacion": numAut,
                    "Razon Social": razSoc,
                    "RUC": numRuc,
                    "Fecha de Emision": fecEmi,
                    "Numero de Documento": numFac,
                    "Fecha de Documento": fechaDoc,
                    "Periodo Fiscal": perFis,
                    "Base Imponible": float(impuesto.baseimponible.string),
                    "Codigo": impuesto.codigo.string,
                    "Impuesto": tipo_impuesto,
                    "Porcentaje": float(impuesto.porcentajeretener.string),
                    "Valor Retenido": float(impuesto.valorretenido.string)
                })
            print("-----Retenciones-----")
            for retencion in retenciones:
                print(f"""
                Base Imponible: {retencion["Base Imponible"]}
                Codigo: {retencion["Codigo"]}
                Impuesto: {retencion["Impuesto"]}
                Porcentaje: {retencion["Porcentaje"]}
                Valor Retenido: {retencion["Valor Retenido"]}
                """)
    except Exception as error:
        print(f"Hubo un error en el documento{filename}, se omite. {error}")
        retenciones.append({
                    "Numero de Autorizacion": "00000",
                    "Razon Social": "ERROE",
                    "RUC": "00000",
                    "Fecha de Emision": "-",
                    "Numero de Documento": "-",
                    "Fecha de Documento": "-",
                    "Periodo Fiscal": "-",
                    "Base Imponible": 0,
                    "Codigo": "0",
                    "Impuesto": "-",
                    "Porcentaje": 0,
                    "Valor Retenido": 0
                })
    return retenciones
            
            

def export(scrapped: list, type:str) -> None:
    if type == "Factura":
        csv_file = "CuadroFacturas.xlsx"
        df = pd.DataFrame(scrapped)

        df["RUC del vendedor"] = df["RUC del vendedor"].map("{}".format)
        df["Numero de Autorizacion"] = df["Numero de Autorizacion"].map("{}".format)
        df["IVA 12%"] = df["IVA 12%"].round(2)
        df["Total sin descuento"] = df["Total sin descuento"].round(2)

        convert_dict = {"RUC del vendedor": str, "Numero de Autorizacion": str}
        df = df.astype(convert_dict)
    elif type == "Retencion":
        csv_file = "CuadroRetenciones.xlsx"
        df = pd.DataFrame(scrapped)

        df["RUC"] = df["RUC"].map("{}".format)
        df["Numero de Autorizacion"] = df["Numero de Autorizacion"].map("{}".format)
        df["Numero de Documento"] = df["Numero de Documento"].map("{}".format)
        df["Base Imponible"] = df["Base Imponible"].round(2)
        df["Porcentaje"] = df["Porcentaje"].round(2)
        df["Valor Retenido"] = df["Valor Retenido"].round(2)


    filepath = Path(path + "/" + csv_file)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(filepath, index=False)


if __name__ == "__main__":
    content_invoice = []
    content_receipt = []
    for filename in glob.glob(os.path.join(path, "*.xml")):
        print("\n----------", filename.split(os.sep)[1], "-----\n")
        print(filename)
        try:
            if "Factura" in filename:
                scrapped = parse_xml_invoice(filename)
                content_invoice.append(scrapped)
            elif "Comprobante" in filename:
                scrapped = parse_xml_receipt(filename)
                for dic in scrapped:
                    content_receipt.append(dic)
        except Exception as error:
            print("Hubo un problema con el archivo " + filename.split(os.sep)[1])
            print(error)
            traceback.print_exc()
    
    if content_invoice:
        export(content_invoice, "Factura")
    else:
        print("No se encontraron facturas")
    
    if content_receipt:
        export(content_receipt, "Retencion")
    else:
        print("No se encontraron retenciones")

