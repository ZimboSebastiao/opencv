# Análise de Pele com Flask e OpenCV

## Descrição

Este repositório contém um backend desenvolvido em Python utilizando **Flask** e **OpenCV** para a análise de pele a partir de imagens capturadas. A aplicação realiza a decodificação de imagens em formato base64, processa-as para determinar características da pele e fornece recomendações através de integração com o assistente **Gemini**.

## Funcionalidades

- **Decodificação de Imagens**: Recebe imagens em formato base64 e realiza a decodificação, transformando-as em um formato utilizável para processamento.
- **Análise de Pele**: O servidor analisa a pele para determinar:

  - **Tipo de Pele**: Classificação em seca, mista ou oleosa com base em medidas de intensidade de cor.
  - **Análise de Cor**: Cálculo da média de matiz, saturação e valor da imagem da pele.
  - **Detecção de Problemas**: Identificação de manchas e problemas na pele, como manchas de sol ou acne.
  - **Análise de Textura**: Avaliação da textura da pele, classificando-a como boa, razoável ou ruim.

- **Geração de Respostas**: Envia os resultados da análise para o assistente **Gemini**, que fornece interpretações e recomendações personalizadas para cuidados com a pele.

- **Registro de Resultados**: Todas as análises são registradas em logs para auditoria e acompanhamento futuro.

- **Uso de Variáveis de Ambiente**: A chave da API é carregada a partir de um arquivo `.env`, garantindo maior segurança e praticidade na configuração.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação utilizada para o desenvolvimento do servidor.
- **Flask**: Microframework web para Python que permite a criação de APIs de forma rápida e eficiente.
- **OpenCV**: Biblioteca de visão computacional que fornece as ferramentas necessárias para o processamento de imagens.
- **NumPy**: Biblioteca fundamental para computação científica, utilizada para manipulação de arrays.
- **Pillow**: Biblioteca de manipulação de imagens em Python.
- **Requests**: Biblioteca para fazer requisições HTTP, utilizada para a comunicação com a API do Gemini.
- **python-dotenv**: Biblioteca para carregar variáveis de ambiente a partir de arquivos `.env`.

## Como Executar

1. **Clone o repositório**:

   ```bash
   git clone <URL do repositório>
   cd <nome do repositório>
   ```

2. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Crie um arquivo `.env`**:

   - Crie um arquivo chamado `.env` na raiz do projeto e adicione a seguinte linha, substituindo `YOUR_API_KEY` pela sua chave da API:
     ```
     API_KEY=YOUR_API_KEY
     ```

4. **Execute o servidor**:

   ```bash
   python app.py
   ```

5. **Acesse a API**:
   - A API estará disponível em `http://localhost:5000/analyze-skin`.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um pull request ou reportar problemas.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

```

Sinta-se à vontade para modificar qualquer parte para refletir com precisão o que você deseja comunicar! Se precisar de mais alguma coisa, estou à disposição.


```
