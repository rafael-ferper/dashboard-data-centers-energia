# Subir o dashboard e deixar pronto para quinta

Tempo estimado: 20 a 30 minutos. Faça hoje inteiro, não pare no meio.

---

## Etapa 0 — Testar local primeiro (5 min)

Não pule. Se quebrar, quebra aqui e não na sala de aula.

```powershell
cd caminho\para\a\pasta
pip install -r requirements.txt
streamlit run app.py
```

Abre em `localhost:8501`. Se os 6 gráficos aparecerem, siga. Se der erro, resolva antes de subir.

---

## Etapa 1 — Criar o repositório no GitHub (5 min)

1. No GitHub: **New repository**
2. Nome sugerido: `dashboard-data-centers-energia`
3. **Público.** O Community Cloud funciona com repositório privado, mas exige permissões de OAuth mais amplas. Como não há nada sensível aqui, público é mais simples.
4. **Não** marque "Add a README" nem "Add .gitignore" — já temos os dois. Marcar cria conflito no primeiro push.

---

## Etapa 2 — Push (5 min)

Na pasta do projeto:

```bash
git init
git add .
git commit -m "Dashboard Atividade 1: data centers e consumo elétrico"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/dashboard-data-centers-energia.git
git push -u origin main
```

Confira no GitHub que estes arquivos subiram:

```
app.py
requirements.txt
electricity_data_center_consumption.csv
.streamlit/config.toml
README.md
.gitignore
```

Se o `.streamlit/` não aparecer, é porque o Git às vezes esconde pastas com ponto na
interface. Confirme com `git ls-files`.

---

## Etapa 3 — Deploy no Streamlit Community Cloud (10 min)

1. Vá em **share.streamlit.io** e entre com a conta do GitHub
2. Autorize o acesso (o Community Cloud precisa ler o código e gerenciar chaves públicas do repositório)
3. **Deploy an app** → **Use existing repo**
4. Preencha:
   - Repository: `SEU_USUARIO/dashboard-data-centers-energia`
   - Branch: `main`
   - Main file path: `app.py`
5. **App URL:** escolha um subdomínio legível, tipo `datacenters-energia`. Sem isso a URL vira um amontoado com hash. Você vai digitar essa URL na frente da turma.
6. Em **Advanced settings**, confira a versão do Python. O padrão é 3.12 e serve.
7. **Deploy**

Leva alguns minutos. Se falhar, os logs ficam à direita da tela e só quem tem acesso de escrita ao repositório consegue ver.

---

## Etapa 4 — Blindagem para quinta (10 min)

**Teste em outra máquina ou no celular.** Abra a URL fora do seu computador. É o teste que importa: se abre no celular, abre na sala.

**Salve a URL em três lugares:** anotada no papel, no bloco de notas do celular, e mandada para você mesmo no WhatsApp. A URL é a única coisa que você não pode esquecer.

**Plano B, 10 minutos:** com o app rodando, tire print dos 6 gráficos e monte um PDF na ordem
dos blocos. Se a internet da sala cair, você apresenta pelo PDF. O enunciado pede o
dashboard acessível, então o PDF é rede de segurança, não substituto.

**Plano C:** deixe o projeto rodando local também. `streamlit run app.py` sem internet
funciona igual.

---

## Se precisar alterar algo depois

```bash
git add .
git commit -m "ajuste de layout"
git push
```

O Community Cloud detecta o push e reconstrói sozinho. Só não faça mais de cinco
atualizações por minuto, que é o limite deles.

---

## Antes de quinta, ainda falta

- Verificar os três números marcados `[VERIFICAR]` no `app.py`
- Acrescentar o contraponto do Idec no bloco 4 (hoje só tem o número da Brasscom, que é parte interessada)
- Ensaiar os 10 minutos com cronômetro
- Ler a tabela decisão → conceito no `README.md`; é a sua folha de defesa na avaliação cruzada

## Ressalva

Confirmei o fluxo de deploy na documentação oficial do Streamlit hoje, mas planos e
limites de serviços gratuitos mudam. Se a tela não bater com estes passos, siga o que
estiver na tela: a lógica (repositório público com `requirements.txt` → conectar → escolher
arquivo de entrada) tende a permanecer.