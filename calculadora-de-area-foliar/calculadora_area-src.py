import os
import cv2
import numpy as np
import csv
import math
import locale  # <--- ALTERAÇÃO: Importa a biblioteca de localização
from tkinter import Tk, simpledialog, filedialog

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV_SAIDA = 'resultados_area_interativo.csv'
LARGURA_JANELA = 1280
ALTURA_JANELA = 720
# --- FIM DAS CONFIGURAÇÕES ---

# Dicionário global para uma gestão de estado mais limpa e profissional
ui_state = {
    "ref_points": [],
    "drawing": False,
    "panning": False,
    "pan_start_pos": (0, 0),
    "offset_x": 0.0,
    "offset_y": 0.0,
    "zoom": 1.0,
    "full_img": None,
    "mouse_pos": (0, 0)
}


def mouse_callback(event, x, y, flags, param):
    """
    Função de callback do mouse, reescrita para uma interatividade profissional.
    Gerencia zoom, pan (arrastar) e desenho da linha de calibração.
    """
    global ui_state

    ui_state["mouse_pos"] = (int(ui_state["offset_x"] + x / ui_state["zoom"]),
                             int(ui_state["offset_y"] + y / ui_state["zoom"]))

    if event == cv2.EVENT_MOUSEWHEEL:
        img_coord_before_zoom_x = ui_state["offset_x"] + x / ui_state["zoom"]
        img_coord_before_zoom_y = ui_state["offset_y"] + y / ui_state["zoom"]

        if flags > 0:
            ui_state["zoom"] *= 1.2
        else:
            ui_state["zoom"] /= 1.2
        ui_state["zoom"] = max(0.1, min(ui_state["zoom"], 20.0))

        img_coord_after_zoom_x = ui_state["offset_x"] + x / ui_state["zoom"]
        img_coord_after_zoom_y = ui_state["offset_y"] + y / ui_state["zoom"]

        ui_state["offset_x"] += (img_coord_before_zoom_x - img_coord_after_zoom_x)
        ui_state["offset_y"] += (img_coord_before_zoom_y - img_coord_after_zoom_y)

    if event == cv2.EVENT_RBUTTONDOWN:
        ui_state["panning"] = True
        ui_state["pan_start_pos"] = (x, y)

    if ui_state["panning"]:
        dx = x - ui_state["pan_start_pos"][0]
        dy = y - ui_state["pan_start_pos"][1]
        ui_state["offset_x"] -= dx / ui_state["zoom"]
        ui_state["offset_y"] -= dy / ui_state["zoom"]
        ui_state["pan_start_pos"] = (x, y)

    if event == cv2.EVENT_RBUTTONUP:
        ui_state["panning"] = False

    img_x, img_y = ui_state["mouse_pos"]

    if event == cv2.EVENT_LBUTTONDOWN:
        ui_state["ref_points"] = [(img_x, img_y)]
        ui_state["drawing"] = True

    if event == cv2.EVENT_LBUTTONUP:
        if ui_state["drawing"]:
            ui_state["ref_points"].append((img_x, img_y))
            ui_state["drawing"] = False


def calcular_area_preta(imagem_cinza, pixels_por_cm):
    """Calcula a área física preta e a proporção da área total."""
    limiar = 50
    _, img_binaria = cv2.threshold(imagem_cinza, limiar, 255, cv2.THRESH_BINARY_INV)
    area_em_pixels = cv2.countNonZero(img_binaria)

    area_pixel_em_cm2 = (1 / pixels_por_cm) ** 2
    area_em_cm2 = area_em_pixels * area_pixel_em_cm2

    total_pixels = imagem_cinza.size
    proporcao = (area_em_pixels / total_pixels) * 100 if total_pixels > 0 else 0

    return area_em_cm2, proporcao


def main():
    """Função principal que orquestra o processo."""
    global ui_state

    # --- ALTERAÇÃO: Define a localização para a do sistema do usuário ---
    # Isso garante que a formatação de números (ponto vs. vírgula) seja correta.
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print("Aviso: Não foi possível definir a localidade do sistema. Usando formatação padrão.")

    root = Tk()
    root.withdraw()

    print("Por favor, selecione a pasta que contém suas imagens.")
    pasta_imagens = filedialog.askdirectory(title="Selecione a pasta de imagens")
    if not pasta_imagens:
        print("Nenhuma pasta selecionada. Encerrando.")
        return

    print("Agora, selecione uma imagem DENTRO desta pasta para a calibração.")
    caminho_referencia = filedialog.askopenfilename(
        title="Selecione a imagem de referência", initialdir=pasta_imagens,
        filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tif")]
    )
    if not caminho_referencia:
        print("Nenhuma imagem de referência selecionada. Encerrando.")
        return

    img_ref = cv2.imread(caminho_referencia)
    if img_ref is None:
        print(f"Erro: Não foi possível carregar a imagem de referência: {caminho_referencia}")
        return

    ui_state["full_img"] = img_ref

    window_name = "Calibracao | Zoom: Roda do Mouse ou +/- | Arrastar: Botao Direito | Desenhar: Botao Esquerdo"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("\n--- INSTRUÇÕES DE CALIBRAÇÃO ---")
    print("1. ZOOM: Roda do mouse ou teclas '+' e '-'.")
    print("2. NAVEGAR: Arrastar com o botão DIREITO do mouse.")
    print("3. DESENHAR: Arrastar com o botão ESQUERDO do mouse.")
    print("4. Após desenhar, pressione 'Enter' ou 'Espaço' para confirmar.")
    print("5. Pressione 'q' para sair.")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('+') or key == ord('='):
            ui_state["zoom"] *= 1.2
            ui_state["zoom"] = min(ui_state["zoom"], 20.0)
        elif key == ord('-'):
            ui_state["zoom"] /= 1.2
            ui_state["zoom"] = max(ui_state["zoom"], 0.1)

        img_h, img_w = ui_state["full_img"].shape[:2]

        visible_w = LARGURA_JANELA / ui_state["zoom"]
        visible_h = ALTURA_JANELA / ui_state["zoom"]
        max_offset_x = max(0, img_w - visible_w)
        max_offset_y = max(0, img_h - visible_h)
        ui_state["offset_x"] = max(0, min(ui_state["offset_x"], max_offset_x))
        ui_state["offset_y"] = max(0, min(ui_state["offset_y"], max_offset_y))

        M = np.array([
            [ui_state["zoom"], 0, -ui_state["offset_x"] * ui_state["zoom"]],
            [0, ui_state["zoom"], -ui_state["offset_y"] * ui_state["zoom"]]
        ], dtype=np.float32)

        viewport = cv2.warpAffine(
            ui_state["full_img"], M, (LARGURA_JANELA, ALTURA_JANELA),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)
        )

        p1_img, p2_img = None, None
        if len(ui_state["ref_points"]) > 0:
            p1_img = ui_state["ref_points"][0]
            if len(ui_state["ref_points"]) == 2:
                p2_img = ui_state["ref_points"][1]
            elif ui_state["drawing"]:
                p2_img = ui_state["mouse_pos"]

        if p1_img and p2_img:
            p1_view = (int((p1_img[0] - ui_state["offset_x"]) * ui_state["zoom"]),
                       int((p1_img[1] - ui_state["offset_y"]) * ui_state["zoom"]))
            p2_view = (int((p2_img[0] - ui_state["offset_x"]) * ui_state["zoom"]),
                       int((p2_img[1] - ui_state["offset_y"]) * ui_state["zoom"]))
            cv2.line(viewport, p1_view, p2_view, (0, 0, 255), 2)

        zoom_text = f"Zoom: {ui_state['zoom']:.2f}x"
        cv2.putText(viewport, zoom_text, (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow(window_name, viewport)

        if key == ord('q'):
            cv2.destroyAllWindows()
            print("Calibração cancelada.")
            return

        if len(ui_state["ref_points"]) == 2 and not ui_state["drawing"] and (key == 13 or key == 32):
            break

    cv2.destroyAllWindows()

    if len(ui_state["ref_points"]) != 2:
        print("A linha de calibração não foi definida corretamente.")
        return

    comprimento_real_cm = simpledialog.askfloat(
        "Medida Real", "Qual é o comprimento real (em cm) da linha que você desenhou?", minvalue=0.01
    )
    if not comprimento_real_cm:
        print("Nenhum comprimento fornecido. Encerrando.")
        return

    distancia_pixels = math.sqrt(
        (ui_state["ref_points"][1][0] - ui_state["ref_points"][0][0]) ** 2 +
        (ui_state["ref_points"][1][1] - ui_state["ref_points"][0][1]) ** 2
    )
    pixels_por_cm = distancia_pixels / comprimento_real_cm
    print(f"\nCalibração concluída! Escala: {pixels_por_cm:.2f} pixels por centímetro.")

    resultados = []
    print(f"\nIniciando processamento em lote na pasta '{os.path.basename(pasta_imagens)}'...")

    for nome_arquivo in sorted(os.listdir(pasta_imagens)):
        caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
        if os.path.isfile(caminho_completo) and nome_arquivo.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
            print(f" - Processando: {nome_arquivo}")
            img_cinza = cv2.imread(caminho_completo, cv2.IMREAD_GRAYSCALE)
            if img_cinza is not None:
                area_cm2, proporcao = calcular_area_preta(img_cinza, pixels_por_cm)
                # --- ALTERAÇÃO: Usa a formatação de acordo com a localização do sistema ---
                area_str = locale.format_string('%.4f', area_cm2)
                proporcao_str = locale.format_string('%.2f', proporcao)
                resultados.append([nome_arquivo, area_str, proporcao_str])
            else:
                resultados.append([nome_arquivo, "Erro ao ler imagem", "N/A"])

    try:
        # Usa ponto e vírgula (;) como delimitador para compatibilidade com Excel em português
        with open(ARQUIVO_CSV_SAIDA, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Nome do Arquivo', 'Area Calculada (cm^2)', 'Proporcao da Area Preta/Total (%)'])
            writer.writerows(resultados)
        print(f"\nResultados salvos com sucesso no arquivo '{ARQUIVO_CSV_SAIDA}'!")
    except IOError as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")


if __name__ == '__main__':
    main()