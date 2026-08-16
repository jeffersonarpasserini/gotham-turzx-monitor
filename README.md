# Gotham TURZX Monitor

Um painel duplo para Linux que transforma duas telas USB TURZX/Turing em parte do cenário do computador:

- a tela circular de 2,1″ exibe um emblema de criatura noturna construído com blocos, girando continuamente;
- a tela vertical de 9,2″ exibe uma cidade neo-gótica ao fundo, com CPU, GPU, temperaturas, memória e disco em tempo real.

O projeto foi preparado e testado no Ubuntu 24.04 com estes dispositivos:

| Tela | Identificação USB | Protocolo | Resolução |
|---|---|---|---|
| Turing 2,1″ | `1a86:ca21`, serial `CT21INCH` | serial, revisão C | `480×480` |
| TURZX 9,2″ | `1cbe:0092`, `TURZX1.0` | USB direto | `462×1920` |

> Este projeto não é afiliado à TURZX, Turing, LEGO, DC Comics ou aos fabricantes dos dispositivos. Os visuais incluídos são criações originais e não contêm personagens ou logotipos oficiais.

## Resultado

### Tela circular

O arquivo [`bat-emblem-spinner.py`](bat-emblem-spinner.py) controla diretamente a tela de 2,1″. Ele carrega o asset `res/custom/bat-emblem-480.png`, gira a imagem em incrementos suaves e envia cada quadro ao display.

### Tela vertical

O tema [`Gotham92`](res/themes/Gotham92/theme.yaml) usa uma composição vertical escura para preservar a leitura das métricas:

- uso e temperatura da CPU;
- uso e temperatura da GPU;
- uso de memória;
- uso de disco.

## Requisitos

- Ubuntu 24.04 ou distribuição Linux equivalente;
- Python 3.9 ou mais recente;
- Git;
- `libusb-1.0-0`;
- duas telas compatíveis conectadas por USB;
- usuário com acesso aos grupos `dialout` e `plugdev`.

## Instalação

Instale os pacotes do sistema:

```bash
sudo apt update
sudo apt install -y git python3-venv libusb-1.0-0
```

Clone o projeto:

```bash
cd ~
git clone https://github.com/jeffersonarpasserini/gotham-turzx-monitor.git
cd gotham-turzx-monitor
```

Crie o ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

## Permissões USB

Instale as regras restritas aos IDs dos displays:

```bash
sudo install -m 0644 99-turing-smart-screen.rules \
  /etc/udev/rules.d/99-turing-smart-screen.rules
sudo usermod -aG dialout,plugdev "$USER"
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Desconecte e reconecte as telas. Em seguida, encerre completamente a sessão do Linux e entre novamente para que os novos grupos sejam aplicados.

Confira:

```bash
groups
ls -l /dev/ttyACM0 /dev/ttyACM1
```

O usuário deve pertencer a `dialout` e `plugdev`.

## Teste da tela menor

Execute:

```bash
cd ~/gotham-turzx-monitor
.venv/bin/python bat-emblem-spinner.py
```

Interrompa com `Ctrl+C`.

Os parâmetros de animação ficam no início do arquivo:

```python
FRAME_SECONDS = 0.12
ROTATION_STEP = 6
```

Um valor menor em `FRAME_SECONDS` aumenta a taxa de atualização. Um valor maior em `ROTATION_STEP` acelera a rotação.

## Teste da tela maior

Execute:

```bash
cd ~/gotham-turzx-monitor
TURING_CONFIG=config-gotham.yaml .venv/bin/python main.py
```

O arquivo [`config-gotham.yaml`](config-gotham.yaml) seleciona:

- revisão `TUR_USB`;
- tema `Gotham92`;
- sensores reais do Linux;
- brilho inicial de 30%.

Interrompa com `Ctrl+C`.

## Prévia sem hardware

É possível renderizar o painel vertical sem escrever no USB:

```bash
TURING_CONFIG=config-gotham-preview.yaml \
  timeout --signal=TERM 8s .venv/bin/python main.py
```

A imagem resultante será gravada em `screencap.png`.

## Inicialização automática

Copie as unidades de usuário:

```bash
mkdir -p ~/.config/systemd/user
cp systemd/gotham-metrics-display.service ~/.config/systemd/user/
cp systemd/brick-emblem-display.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now gotham-metrics-display.service
systemctl --user enable --now brick-emblem-display.service
```

Consulte o estado:

```bash
systemctl --user status gotham-metrics-display.service
systemctl --user status brick-emblem-display.service
```

Acompanhe os logs:

```bash
journalctl --user -u gotham-metrics-display.service -f
journalctl --user -u brick-emblem-display.service -f
```

As unidades pressupõem que o repositório foi clonado em `~/gotham-turzx-monitor`. Ajuste `WorkingDirectory` e `ExecStart` se utilizar outro caminho.

## Personalização

### Brilho

Na tela vertical, altere `BRIGHTNESS` em `config-gotham.yaml`. Na tela circular, altere `SetBrightness(level=35)` em `bat-emblem-spinner.py`.

Evite brilho máximo por longos períodos, principalmente em gabinetes com pouca circulação de ar.

### Rotação física

Para inverter a tela vertical:

```yaml
display:
  DISPLAY_REVERSE: true
```

### Métricas e posições

Edite:

```text
res/themes/Gotham92/theme.yaml
```

O canvas lógico do tema possui `480×1920`. O controlador adapta os 480 pixels lógicos aos 462 pixels físicos do modelo de 9,2″.

## Solução de problemas

### `Access denied (insufficient permissions)`

Confirme que a regra foi instalada e que o usuário relogou:

```bash
ls -l /etc/udev/rules.d/99-turing-smart-screen.rules
groups
```

### Tela circular não encontrada

Confira os estados serial do dispositivo:

```bash
ls -l /dev/serial/by-id/
```

O controlador espera o estado ativo:

```text
usb-Android_Android_20080411-if00
```

Algumas revisões aparecem primeiro como `CT21INCH` e reconectam como `Android 20080411` ao acordar.

### Tela maior não encontrada

Confira:

```bash
lsusb | grep -i -E '1cbe:0092|TURZX'
```

### Métrica de GPU indisponível

O suporte depende do driver e da GPU. CPU, memória e disco continuam funcionando mesmo sem telemetria de GPU. Para NVIDIA, confirme que `nvidia-smi` funciona. Para AMD, confira o acesso aos dispositivos em `/sys/class/drm`.

## Arquitetura

```text
brick-emblem-display.service
└── bat-emblem-spinner.py
    └── Turing 2.1" via serial

gotham-metrics-display.service
└── main.py + config-gotham.yaml
    ├── sensores Linux
    ├── tema Gotham92
    └── TURZX 9.2" via libusb
```

Os displays são controlados por processos independentes para evitar disputa pela porta serial ou pelo dispositivo USB.

## Base e licença

Este repositório deriva de [mathoudebine/turing-smart-screen-python](https://github.com/mathoudebine/turing-smart-screen-python), de Matthieu Houdebine e demais contribuidores. A base original fornece os protocolos USB/serial, sensores, renderizador de temas e suporte multiplataforma.

As modificações deste repositório incluem:

- seleção de arquivo de configuração por `TURING_CONFIG`;
- tema vertical neo-gótico para 9,2″;
- animação independente para a tela circular;
- regras `udev` específicas;
- unidades systemd de usuário;
- assets visuais originais.

O código permanece licenciado sob a **GNU General Public License v3.0**, conforme [`LICENSE`](LICENSE).
