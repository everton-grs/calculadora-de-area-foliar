# Calculadora de área foliar

Script em Python que calcula automaticamente a área física (cm²) e a proporção de pixels pretos em imagens. Inclui interface interativa para calibração de escala, permitindo definir a relação pixels/cm a partir de uma imagem de referência. Pode ser aplicado, por exemplo, na análise do crescimento foliar em plantas. Calcula a soma de todas as folhas presente na imagem carregada.

## Funcionalidades

- Calibração Interativa: Interface visual para desenhar uma linha de referência sobre a imagem e informar seu tamanho real. Conta com recursos de Zoom e Pan (arrastar) para maior precisão.
- Processamento em Lote (Batch): Processa automaticamente todas as imagens da pasta selecionada de uma só vez.
- Limiar de Detecção: Converte as imagens para tons de cinza e identifica como "preto" os pixels com intensidade abaixo de 50.
- Exportação Localizada: Gera um relatório .csv configurado para a localidade do seu sistema (ex: uso de vírgulas para decimais e ponto e vírgula como separador), garantindo compatibilidade nativa e sem desconfigurações com o Microsoft Excel em português.

## Pré-Requisitos

Para rodar este script, você precisará ter o Python 3 instalado em sua máquina, além de algumas bibliotecas externas. 

Você pode instalar as dependências necessárias executando o seguinte comando no seu terminal ou prompt de comando:
pip install opencv-python numpy

ou, ainda, executar o .exe disponibilizado diretamente.

Nota: As bibliotecas os, csv, math, locale e tkinter já vêm embutidas na instalação padrão do Python.


## Como Usar
---------

0. Copie a pasta “Exemplos” ou as suas imagens para medida de área para a área de trabalho do PC ou em outro local fora da pasta raiz da Calculadora de Área Foliar.

1. Execute o script:
   Rode o arquivo calculadora_area.py no seu terminal ou IDE, ou execute o .exe disponibilizado.

2. Selecione o diretório:
   Uma janela se abrirá pedindo para você selecionar a pasta onde estão todas as imagens que deseja analisar. Não coloque essa pasta no mesmo diretório do script calculadora_area.py, pois isso pode causar conflitos no processamento e gerar mensagens de erro.

3. Selecione a imagem de calibração:
   Logo em seguida, outra janela pedirá que você escolha uma imagem específica de dentro dessa pasta para servir de referência. Recomenda-se usar uma imagem que contenha um objeto de tamanho conhecido (como uma régua ou escala).

4. Faça a calibração:
   Uma janela interativa do OpenCV será aberta com a imagem de referência.
   - Zoom: Use a roda do mouse ou as teclas '+' e '-'.
   - Navegar (Pan): Segure o botão direito do mouse e arraste para mover a imagem (útil quando estiver com muito zoom).
   - Desenhar: Clique, segure e arraste o botão esquerdo do mouse para desenhar uma linha sobre a sua referência de tamanho.
   - Confirmar: Após desenhar a linha, pressione 'Enter' ou 'Espaço'. Para cancelar a qualquer momento, pressione 'q'.

5. Informe o tamanho real:
   Uma pequena janela pop-up aparecerá perguntando o tamanho real (em centímetros) da linha que você acabou de desenhar.

6. Aguarde o processamento:
   O script calculará a proporção de pixels/cm e processará todas as imagens da pasta.

7. Verifique os resultados:
   Ao final, um arquivo chamado resultados_area_interativo.csv será criado no mesmo diretório em que o script está sendo executado.


## Interpretando os resultados (Arquivo CSV)
--------------------------------------
O arquivo CSV gerado conterá três colunas:
- Nome do Arquivo: O nome da imagem processada.
- Área Calculada (cm²): A área física total ocupada pelos pixels escuros (intensidade < 50) na imagem.
- Proporção Área Preta/Total (%): A porcentagem da imagem inteira que é composta por esses pixels escuros.
