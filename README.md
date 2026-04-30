# BR Radar Canarinho

Dashboard em Streamlit para atletas cotados para a Seleção Brasileira, com:

- dashboard geral de presença digital simulada;
- escalação 4-3-3 com cards estilo FIFA;
- fotos de jogadores e escudos via TheSportsDB;
- estatísticas simuladas por jogador;
- aba opcional de partidas da Copa via football-data.org.

## Como rodar

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Planilha

Use o arquivo `atletas_com_thesportsdb.xlsx`.

Novas colunas adicionadas:

- `Nome TheSportsDB`: nome usado para buscar foto do jogador;
- `Time TheSportsDB`: nome usado para buscar escudo do clube;
- `Foto Jogador URL`: opcional, use para colocar manualmente uma URL de foto;
- `Escudo Time URL`: opcional, use para colocar manualmente uma URL de escudo.

Se as colunas de URL estiverem vazias, o app tenta buscar automaticamente na TheSportsDB.

## football-data.org

Para ativar a aba de partidas da Copa, crie `.streamlit/secrets.toml` com:

```toml
FOOTBALL_DATA_KEY = "SUA_CHAVE_AQUI"
```
