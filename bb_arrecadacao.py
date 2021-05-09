import requests, csv
from bs4 import BeautifulSoup

def printRequest(r, method, url_solicitada, form = None):
    print('\nURL Solicitada da requisicao: '.ljust(28, ' ') + url_solicitada)
    print('URL Efetiva da requisicao: '.ljust(30, ' ') + r.url)
    print('History redirect: '.ljust(30, ' ') + str(r.history))
    print('Status code: '.ljust(30, ' ') + str(r.status_code) + '\tReason: ' + str(r.reason))
    print('Elapsed: '.ljust(30, ' ') + str(r.elapsed) + '\tEnconding: ' + str(r.encoding))
    if form != None:
        printForm(form)
    print('\nOs headers da requisicao do ' + method + ' sao: ' + '\n')
    print("\n".join("{} {}".format(k.ljust(28, ' '), v.ljust(30, ' ')) for k, v in r.request.headers.items()))
    print('\nOs headers da resposta do ' + method + ' sao: ' + '\n')
    print("\n".join("{} {}".format(k.ljust(28, ' '), v.ljust(30, ' ')) for k, v in r.headers.items()))
    print('\n' + ''.ljust(158, '='))
    
    
def printForm(form):
    print('\nForm da requisicao:')
    print("\n".join("{} ".format(k) for k in form.items()))

def get_html_bb_arrecadacao(nome_municipio, data_busca_inicial, data_busca_final):

    with requests.Session() as session:
        
        # session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'})

        url_custom = 'https://www42.bb.com.br/portalbb/daf/beneficiario,802,4647,4652,0,1.bbx'
        r = session.get(url_custom)
        # printRequest(r, 'GET', url_custom)

        soup = BeautifulSoup(r.content, "html.parser")
        publicadorformvalue = soup.find_all("input")[0].attrs['value']
        javaxFacesViewState = soup.find_all("input")[8].attrs['value']

        form = {    'publicadorformvalue': publicadorformvalue, \
                    'formulario:txtBenef': nome_municipio, \
                    'formulario:j_id16': 'Continuar', \
                    'formulario': 'formulario', \
                    'autoScroll': '', \
                    'javax.faces.ViewState': javaxFacesViewState    }

        cookie_dict =  session.cookies.get_dict()
        url_custom = 'https://www42.bb.com.br/portalbb/daf/beneficiario.bbx' + ';jsessionid=' + cookie_dict['JSESSIONID']
        
        r = session.post(url_custom, data=form, allow_redirects = True)
        # printRequest(r, 'POST', url_custom, form=form)
        # r = session.get(r.url)
        # printRequest(r, 'GET', url_custom)

        soup = BeautifulSoup(r.content, "html.parser")
        publicadorformvalue = soup.find_all("input")[0].attrs['value']
        codigoMunicipio = soup.find_all("option")[0].attrs['value']
        comboFundo ='org.jboss.seam.ui.NoSelectionConverter.noSelectionValue'
        javaxFacesViewState = soup.find_all("input")[9].attrs['value']

        form = {    'publicadorformvalue': publicadorformvalue, \
                    'formulario:comboBeneficiario': codigoMunicipio, \
                    'formulario:dataInicial': data_busca_inicial, \
                    'formulario:dataFinal': data_busca_final, \
                    'formulario:comboFundo': comboFundo, \
                    'formulario:j_id20': 'Continuar', \
                    'formulario': 'formulario', \
                    'autoScroll': '', \
                    'javax.faces.ViewState': javaxFacesViewState    }

        url_custom = 'https://www42.bb.com.br/portalbb/daf/beneficiarioList.bbx' + ';jsessionid=' + cookie_dict['JSESSIONID']

        r = session.post(url_custom, data=form, allow_redirects = True)
        # printRequest(r, 'POST', url_custom, form=form)

        return r.content


def processa(nome_municipio, data_pesquisa_inicial, data_pesquisa_final):

    html = get_html_bb_arrecadacao( nome_municipio, data_pesquisa_inicial, data_pesquisa_final )
    soup = BeautifulSoup(html, "html.parser")

    fundos = []
    tags_fundos = soup.find_all(attrs={"class": "rich-table-row even"})
    for tag_fundo in tags_fundos:
        temp = tag_fundo.string
        fundos.append(" ".join(temp.split()))

    # remove ultima tag
    fundos = fundos[:-1] 

    tags_tds = soup.find_all('td')
    # busca valor total recebido
    valor_total_recebido = tags_tds[len(tags_tds) - 1].string.replace('R$','').replace(' C', '').strip() 

    # alinhamento = 27
    # print(''.ljust(60, '='))
    # print('Nome municipio:'.ljust(alinhamento, ' ') + nome_municipio.upper())
    # print('Periodo de busca:'.ljust(alinhamento, ' ') + data_pesquisa_inicial + ' ate ' + data_pesquisa_final)
    # print('Recurso total recebido:'.ljust(alinhamento, ' ') + valor_total_recebido)
    # print('Fontes dos recursos:'.ljust(alinhamento, ' ') + '{}'.format(fundos))

    return valor_total_recebido, fundos

def read_input_municipios():
    f = open("input_municipios.txt", "r")
    municipios = []
    for line in f:
        temp = " ".join(line.split()).replace('\n','').encode("ascii", errors="ignore").decode()
        municipios.append(temp)
    
    return municipios

data_inicial = '07/03/2021'
data_final = '06/05/2021'

municipios = read_input_municipios()

with open('arrecadacao.csv', mode='w', newline='') as arrecadacao_file:
    
    wr = csv.writer(arrecadacao_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    for municipio in municipios:
        valor, fundos = processa(municipio, data_inicial, data_final)
        row = [municipio.upper(), valor, fundos]
        wr.writerow(row)


        
