import tkinter as tk
from tkinter import filedialog, messagebox
from fpdf import FPDF
import xml.etree.ElementTree as ET

class XMLtoPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor XML para PDF ")
        self.root.geometry("400x200") 

        self.label_xml = tk.Label(root, text="Arquivo XML selecionado:")
        self.label_xml.pack()

        self.selected_xml_label = tk.Label(root, text="")
        self.selected_xml_label.pack()

        self.btn_xml = tk.Button(root, text="Selecionar XML", command=self.select_xml_file)
        self.btn_xml.pack()

        self.label_output = tk.Label(root, text="Pasta de saída:")
        self.label_output.pack()

        self.selected_output_label = tk.Label(root, text="")
        self.selected_output_label.pack()

        self.btn_output = tk.Button(root, text="Selecionar Pasta", command=self.select_output_location)
        self.btn_output.pack()

        self.btn_convert = tk.Button(root, text="Converter para PDF", command=self.convert_to_pdf)
        self.btn_convert.pack()


    def select_xml_file(self):
        self.xml_path = filedialog.askopenfilename(title="Selecione o arquivo XML")
        self.selected_xml_label.config(text=self.xml_path)
    
    def select_output_location(self):
        self.output_folder = filedialog.askdirectory(title="Selecione a pasta de saída")
        self.selected_output_label.config(text=self.output_folder)

    def convert_to_pdf(self):
        if not hasattr(self, 'xml_path') or not hasattr(self, 'output_folder'):
            messagebox.showerror("Erro", "Por favor, selecione tanto o arquivo XML quanto a pasta de saída.")
            return

        informacoes_nota = self.extract_information_from_xml(self.xml_path)
        pdf_path = self.output_folder + "/nota_fiscal.pdf"
        self.create_pdf(informacoes_nota, pdf_path)
        messagebox.showinfo("Conversão Concluída", "A nota fiscal foi convertida para PDF com sucesso!")
        
    def extract_information_from_xml(self, xml_path):
        informacoes = {}
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}  
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Extração das informações básicas (exemplo: emitente, destinatário)
        for child in root.findall('.//nfe:infNFe', ns):
            for info in child:
                if info.tag.endswith('emit') or info.tag.endswith('dest'):
                    # Trata informações - emitente e destinatário
                    section_info = {}
                    for detail in info:
                        detail_tag = detail.tag.replace('{http://www.portalfiscal.inf.br/nfe}', '')
                        if detail.tag.endswith('enderEmit') or detail.tag.endswith('enderDest'):
                            # Endereço do emitente ou destinatário
                            address_info = {}
                            for address_detail in detail:
                                address_tag = address_detail.tag.replace('{http://www.portalfiscal.inf.br/nfe}', '')
                                address_info[address_tag] = address_detail.text
                            section_info[detail_tag] = address_info
                        else:
                            section_info[detail_tag] = detail.text
                    informacoes[info.tag.replace('{http://www.portalfiscal.inf.br/nfe}', '')] = section_info
                elif info.tag.endswith('det'):
                    # Trata detalhes dos produtos
                    if 'prod' not in informacoes:
                        informacoes['prod'] = []
                    prod_info = {}
                    imposto_info = {}
                    for prod_or_imposto in info:
                        if prod_or_imposto.tag.endswith('prod'):
                            for prod_detail in prod_or_imposto:
                                prod_tag = prod_detail.tag.replace('{http://www.portalfiscal.inf.br/nfe}', '')
                                prod_info[prod_tag] = prod_detail.text
                        elif prod_or_imposto.tag.endswith('imposto'):
                            for imposto_detail in prod_or_imposto:
                                imposto_tag = imposto_detail.tag.replace('{http://www.portalfiscal.inf.br/nfe}', '')
                                imposto_info[imposto_tag] = "Informação de imposto"  
                    informacoes['prod'].append({'prod_info': prod_info, 'imposto_info': imposto_info})

        return informacoes

    def create_pdf(self, informacoes, pdf_path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for section, details in informacoes.items():
            if section in ['emit', 'dest']:
                pdf.cell(0, 10, f"{section.upper()}:", 0, 1)
                for key, value in details.items():
                    if isinstance(value, dict):  
                        for sub_key, sub_value in value.items():
                            pdf.cell(0, 10, f"{sub_key}: {sub_value}", 0, 1)
                    else:
                        pdf.cell(0, 10, f"{key}: {value}", 0, 1)
                pdf.cell(0, 10, "", 0, 1) 

            elif section == 'prod':
                pdf.cell(0, 10, "PRODUTOS:", 0, 1)
                for product in details:
                    pdf.set_font("Arial", 'B', 12)  
                    pdf.cell(0, 10, f"Produto {details.index(product) + 1}", 0, 1)
                    pdf.set_font("Arial", size=12)  
                    for prod_key, prod_value in product['prod_info'].items():
                        pdf.cell(0, 10, f"{prod_key}: {prod_value}", 0, 1)
                    
                    pdf.cell(0, 10, "Imposto:", 0, 1)
                    for imposto_key, imposto_value in product['imposto_info'].items():
                        pdf.cell(0, 10, f"{imposto_key}: {imposto_value}", 0, 1)
                    
                    pdf.cell(0, 10, "", 0, 1)  

        pdf.output(pdf_path)


def main():
    root = tk.Tk()
    app = XMLtoPDFConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()