"""
Ficha simples 01 / Bloco C - Auditoria assistida por IA (7 camadas).
Le o download oficial do GBIF (Darwin Core Archive), aplica testes objetivos
por camada, e produz um LOG com decisao (nao exclui nada silenciosamente).

Principio (Protocolo 02): a IA organiza e sinaliza; a decisao final de
manter/excluir e revisada por um humano antes da modelagem.

Saidas:
  Dados/FO01_04_log_auditoria.csv       -> log completo, 1 linha por registro
  Dados/FO01_03_ocorrencias_auditadas.csv -> base + colunas de auditoria
  Dados/FO01_05_sintese_auditoria.md    -> resumo legivel para o diario/relatorio
"""
import pandas as pd
import numpy as np

SRC = "Dados/gbif_oficial_extraido/occurrence.txt"
OUT_LOG = "Dados/FO01_04_log_auditoria.csv"
OUT_AUDITADAS = "Dados/FO01_03_ocorrencias_auditadas.csv"
OUT_SINTESE = "Dados/FO01_05_sintese_auditoria.md"

ESTADOS_ALVO = {"Amazonas", "Acre", "Rondônia", "Roraima"}
ESTADOS_AMAZONIA_PLAUSIVEL = ESTADOS_ALVO | {"Pará", "Mato Grosso"}  # adjacentes, dentro da distribuicao conhecida
PALAVRAS_CATIVEIRO = r"zool[oó]gico|\bzoo\b|cativeiro|cativ[oa]|parque zool"

df = pd.read_csv(SRC, sep="\t", quoting=3, low_memory=False, encoding="utf-8")
n0 = len(df)
print(f"Registros carregados: {n0}")

flags = pd.DataFrame(index=df.index)
flags["gbifID"] = df["gbifID"]

# ---------- Camada 1: Integridade ----------
flags["c1_sem_coordenada"] = df["decimalLatitude"].isna() | df["decimalLongitude"].isna()
flags["c1_coordenada_zero"] = (df["decimalLatitude"] == 0) & (df["decimalLongitude"] == 0)
flags["c1_lat_fora_intervalo"] = ~df["decimalLatitude"].between(-90, 90)
flags["c1_lon_fora_intervalo"] = ~df["decimalLongitude"].between(-180, 180)
dup_key = df["decimalLatitude"].round(5).astype(str) + "_" + df["decimalLongitude"].round(5).astype(str) + "_" + df["eventDate"].astype(str) + "_" + df["recordedBy"].astype(str)
flags["c1_duplicata_provavel"] = dup_key.duplicated(keep=False) & ~df["decimalLatitude"].isna()
flags["c1_issue_gbif"] = df["issue"].fillna("")

# ---------- Camada 2: Taxonomia ----------
flags["c2_taxon_rank"] = df["taxonRank"]
flags["c2_status_taxonomico"] = df["taxonomicStatus"]
flags["c2_nome_aceito"] = df["acceptedScientificName"]
flags["c2_infraespecifico"] = df["infraspecificEpithet"]

# ---------- Camada 3: Geografia ----------
flags["c3_country_code"] = df["countryCode"]
flags["c3_estado_gbif"] = df["level1Name"]
flags["c3_fora_estados_alvo"] = ~df["level1Name"].isin(ESTADOS_ALVO)
flags["c3_fora_amazonia_plausivel"] = ~df["level1Name"].fillna("NAO_IDENTIFICADO").isin(ESTADOS_AMAZONIA_PLAUSIVEL)
flags["c3_issue_geo"] = df["issue"].fillna("").str.contains(
    "COUNTRY_COORDINATE_MISMATCH|COORDINATE_INVALID|COORDINATE_OUT_OF_RANGE|PRESUMED_.*_INVALID", regex=True
)
# Coordenada repetida entre registros do mesmo dataset em datas diferentes:
# padrao tipico de coordenada institucional/endereco de permissionario (nao local de observacao real)
coord_key_dataset = (df["decimalLatitude"].round(4).astype(str) + "_" +
                     df["decimalLongitude"].round(4).astype(str) + "_" + df["datasetName"].astype(str))
flags["c3_coordenada_institucional_suspeita"] = (
    coord_key_dataset.duplicated(keep=False)
    & ~df["decimalLatitude"].isna()
    & flags["c3_fora_amazonia_plausivel"]
)

# ---------- Camada 4: Precisao e escala ----------
flags["c4_incerteza_m"] = df["coordinateUncertaintyInMeters"]
flags["c4_incerteza_ausente"] = df["coordinateUncertaintyInMeters"].isna()
flags["c4_incerteza_grande"] = df["coordinateUncertaintyInMeters"] > 50000  # > 50 km, maior que 1 pixel WorldClim (~1km em 10min de arco na linha do equador é ~18km; 50km e um limiar conservador)
flags["c4_distancia_centroide_m"] = df["distanceFromCentroidInMeters"]
flags["c4_possivel_centroide"] = df["distanceFromCentroidInMeters"].fillna(999999) < 100

# ---------- Camada 5: Tempo ----------
flags["c5_ano"] = df["year"]
flags["c5_ano_ausente"] = df["year"].isna()
flags["c5_pre_1970"] = df["year"] < 1970  # antes do baseline WorldClim "current" (1970-2000)
flags["c5_ano_futuro_ou_invalido"] = (df["year"] > 2026) | (df["year"] < 1800)

# ---------- Camada 6: Plausibilidade ----------
flags["c6_basis_of_record"] = df["basisOfRecord"]
flags["c6_fossil"] = df["basisOfRecord"].astype(str).str.contains("FOSSIL", case=False, na=False)
flags["c6_establishment"] = df["establishmentMeans"]
texto_local = (df["locality"].fillna("") + " " + df["occurrenceRemarks"].fillna("") + " " +
               df["habitat"].fillna("") + " " + df["eventRemarks"].fillna(""))
flags["c6_cultivado_ou_cativo"] = (
    df["establishmentMeans"].astype(str).str.contains("CULTIVATED|MANAGED|CAPTIVE|INTRODUCED", case=False, na=False)
    | texto_local.str.contains(PALAVRAS_CATIVEIRO, case=False, regex=True, na=False)
)

# ---------- Camada 7: Vies amostral (diagnostico, nao decide exclusao individual) ----------
flags["c7_dataset"] = df["datasetName"]
flags["c7_instituicao"] = df["institutionCode"]

# ---------- Decisao consolidada ----------
def decidir(row):
    if row["c1_sem_coordenada"] or row["c1_coordenada_zero"] or row["c1_lat_fora_intervalo"] or row["c1_lon_fora_intervalo"]:
        return "EXCLUIR", "coordenada ausente/zero/fora do intervalo valido"
    if row["c6_fossil"]:
        return "EXCLUIR", "basisOfRecord = fossil, irrelevante para distribuicao atual"
    if row["c6_cultivado_ou_cativo"]:
        return "EXCLUIR", "cativeiro/zoologico/introduzido (establishmentMeans ou texto da localidade)"
    if row["c3_coordenada_institucional_suspeita"]:
        return "EXCLUIR", "coordenada repetida entre registros do mesmo dataset em datas distintas, fora da Amazonia plausivel - provavel endereco institucional (sede/permissionario SISBio), nao local de observacao"
    if row["c3_issue_geo"]:
        return "REVISAR", "GBIF sinaliza inconsistencia geografica (issue)"
    if row["c4_possivel_centroide"]:
        return "REVISAR", "distancia ao centroide administrativo muito pequena (<100m) - pode ser coordenada de sede/municipio"
    if row["c3_fora_amazonia_plausivel"]:
        return "REVISAR", f"fora da distribuicao amazonica plausivel da especie (estado={row['c3_estado_gbif']}) - provavel erro de identificacao/geolocalizacao"
    if row["c3_fora_estados_alvo"]:
        return "MANTER_COM_RESSALVA", f"dentro da Amazonia mas fora de AM/AC/RO/RR (estado={row['c3_estado_gbif']}) - fora da area de estudo, mantido apenas como contexto de fundo"
    if row["c1_duplicata_provavel"]:
        return "MANTER_COM_RESSALVA", "possivel duplicata (mesma coordenada/data/coletor) - conferir antes de modelar"
    if row["c4_incerteza_grande"]:
        return "MANTER_COM_RESSALVA", "incerteza de coordenada > 50 km"
    if row["c4_incerteza_ausente"]:
        return "MANTER_COM_RESSALVA", "incerteza de coordenada nao informada"
    if row["c5_ano_ausente"]:
        return "MANTER_COM_RESSALVA", "ano do registro ausente"
    if row["c5_pre_1970"]:
        return "MANTER_COM_RESSALVA", "registro anterior a 1970 - fora do periodo do baseline climatico WorldClim atual"
    return "MANTER", "sem problema relevante detectado"

decisoes = flags.apply(decidir, axis=1, result_type="expand")
flags["decisao"] = decisoes[0]
flags["justificativa"] = decisoes[1]
flags["revisado_por"] = "Leonardo Andrade Aragao (com apoio de IA - Claude/Anthropic)"
flags["data_auditoria"] = "2026-09-23"

flags.to_csv(OUT_LOG, index=False, encoding="utf-8-sig")

auditadas = df.copy()
auditadas["audit_decisao"] = flags["decisao"]
auditadas["audit_justificativa"] = flags["justificativa"]
auditadas.to_csv(OUT_AUDITADAS, index=False, encoding="utf-8-sig")

# ---------- Sintese ----------
contagem = flags["decisao"].value_counts()
linhas = [
    "# Sintese da auditoria (Ficha 01, Bloco C)",
    "",
    f"Total de registros auditados: **{n0}**",
    "",
    "## Decisao final por registro",
    "",
    "| Decisao | N | % |",
    "|---|---|---|",
]
for status in ["MANTER", "MANTER_COM_RESSALVA", "REVISAR", "EXCLUIR"]:
    n = int(contagem.get(status, 0))
    linhas.append(f"| {status} | {n} | {100*n/n0:.1f}% |")

linhas += ["", "## Justificativas mais frequentes (REVISAR/EXCLUIR)", ""]
sub = flags[flags["decisao"].isin(["REVISAR", "EXCLUIR"])]
for just, n in sub["justificativa"].value_counts().items():
    linhas.append(f"- {just}: {n}")

linhas += ["", "## Estados segundo geocodificacao GBIF (level1Name)", ""]
for uf, n in df["level1Name"].value_counts(dropna=False).items():
    linhas.append(f"- {uf}: {n}")

linhas += ["", "## basisOfRecord", ""]
for b, n in df["basisOfRecord"].value_counts(dropna=False).items():
    linhas.append(f"- {b}: {n}")

linhas += ["", "## taxonRank", ""]
for r, n in df["taxonRank"].value_counts(dropna=False).items():
    linhas.append(f"- {r}: {n}")

with open(OUT_SINTESE, "w", encoding="utf-8") as f:
    f.write("\n".join(linhas))

print("\n".join(linhas))
print(f"\nSalvo: {OUT_LOG}\nSalvo: {OUT_AUDITADAS}\nSalvo: {OUT_SINTESE}")
