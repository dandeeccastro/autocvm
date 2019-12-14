# Auto CVM: RPM de Documentos Públicos

Um script em Python que faz download de documentos na CVM

## Descrição 

Existe muito trabalho de análise de uma quantidade massiva de dados públicos
que poderia ser automatizado com as ferramentas certas.
Esse repositório é uma tentativa minha de mexer com esse mundo, usando meus conhecimentos de Python e resolvendo 
os problemas que a doutoranda que conheço (minha mãe) enfrenta com dados públicos.

## Instalação

Clone o repositório e instale as dependências usando [pip](https://pip.pypa.io/en/stable/)

```bash
git clone https://github.com/dandeeccastro/autocvm
cd autocvm
pip3 install selenium unidecode
```

## Uso

Dado que fiz isso por um motivo muito específico, não vejo ninguém usando isso aqui.
Mas, caso tenha interesse, só executar o código com Python 3. O código deve criar uma 
pasta *out*, onde os arquivos serão baixados, e criar uma janela do Firefox para poder
manipular o site da CVM de acordo com o script.

```bash
python3 main.py
```

Sabia que, caso queira fazer isso, a quantidade esperada de arquivos é em torno de **2.2GB**.
