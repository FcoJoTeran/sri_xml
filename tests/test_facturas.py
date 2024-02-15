import os

from Facturas import parse_xml, export

def test_parse_xml_rosado():
    # Prepare the source data path
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_path, "fixtures/Factura-rosado.xml")

    # Call the function to be tested
    result = parse_xml(path)

    # Check the result
    assert result["Razon social"] == "CORPORACION EL ROSADO S.A."
    assert result["RUC del vendedor"] == "0990004196001"
    assert result["Fecha de emision"] == "06/01/2023"
    assert result["Numero de factura"] == "005-004-000533948"
    assert result["Numero de Autorizacion"] == "0601202301099000419600120050040005339480053394812"
    assert result["Subtotal 12%"] == 16.69
    assert result["Subtotal 0%"] == 47.68
    assert result["Subtotal sin impuestos"] == 0
    assert result["IVA 12%"] == 2.0028
    assert result["Total sin descuento"] == 66.3728

def test_parse_xml_cafedetere():
    # Prepare the source data path
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_path, "fixtures/Factura-cafedetere.xml")
    
    # Call the function to be tested
    result = parse_xml(path)

    # Check the result
    assert result["Razon social"] == "CAFE DE TERE CAFEDETERE SA"
    assert result["RUC del vendedor"] == "0992255404001"
    assert result["Fecha de emision"] == "11/01/2023"
    assert result["Numero de factura"] == "010-002-000001200"
    assert result["Numero de Autorizacion"] == "1101202301099225540400120100020000012001234567819"
    assert result["Subtotal 12%"] == 16.52
    assert result["Subtotal 0%"] == 0
    assert result["Subtotal sin impuestos"] == 0
    assert result["IVA 12%"] == 1.9824
    assert result["Total sin descuento"] == 18.502399999999998

def test_parse_xml_no_file():
    # Prepare a fake data path
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_path, "fixtures/nofile.xml")

    # Call the function to be tested
    result = parse_xml(path)

    # Check the result
    assert result["Razon social"] == "ERROR"
    assert result["RUC del vendedor"] == "00000"
    assert result["Fecha de emision"] == "00000"
    assert result["Numero de factura"] == "00000"
    assert result["Numero de Autorizacion"] == "00000"
    assert result["Subtotal 12%"] == 0
    assert result["Subtotal 0%"] == 0
    assert result["Subtotal sin impuestos"] == 0
    assert result["IVA 12%"] == 0
    assert result["Total sin descuento"] == 0

def test_export():
    # Prepare the source data path
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_path, "fixtures/Factura-rosado.xml")
    result_rosado = parse_xml(path)
    path = os.path.join(base_path, "fixtures/Factura-cafedetere.xml")
    result_cafedetere = parse_xml(path)

    scrapped = [result_rosado, result_cafedetere]
    
    # Call the function to be tested
    export(scrapped, base_path)

    # Check the result
    assert os.path.exists(os.path.join(base_path, "CuadroImpuestos.xlsx"))
    
    # Clean up the generated file
    os.remove(os.path.join(base_path, "CuadroImpuestos.xlsx"))
    
    # Check if the file was deleted
    assert not os.path.exists(os.path.join(base_path, "CuadroImpuestos.xlsx"))
