# Carregar pacotes
library(raster)
library(ggplot2)
library(ggspatial)
library(sf)

# 1. Definir o diretório principal UMA VEZ
setwd("C:/Users/Usuário/Desktop/análise")

# 2. Ler e preparar o shapefile (Fora do loop, pois não muda)
municipios_cariri <- shapefile("nordeste.shp")
municipios_sf <- st_as_sf(municipios_cariri)

# 3. Criar a pasta onde as imagens serão salvas (se não existir)
if(!dir.exists("mapas_prontos_nordeste")) {
  dir.create("mapas_prontos_nordeste")
}

# 4. Identificar todas as pastas que começam com "base"
pastas <- list.files(pattern = "^base ")

# =========================================================================
# INÍCIO DO LOOP
# =========================================================================
for (pasta in pastas) {
  
  # Extrair o ano do nome da pasta (ex: transforma "base 2010" em "2010")
  ano <- gsub("base ", "", pasta)
  message("Processando o ano: ", ano, "...")
  
  # Registra os arquivos temporários ANTES de criar novos
  temps_antes <- list.files(tempdir(), full.names = TRUE)
  
  # Listar o arquivo .tif dentro da pasta atual
  arquivo_tif <- list.files(path = pasta, pattern = '\\.tif$', full.names = TRUE)
  
  # Se por acaso a pasta estiver vazia, o loop pula para o próximo ano
  if(length(arquivo_tif) == 0) next
  
  # Carregar raster
  dados <- raster::stack(arquivo_tif)
  
  # Crop e mask
  raster_cortado  <- crop(dados, municipios_cariri)
  raster_mascarado <- mask(raster_cortado, municipios_cariri)
  
  # Limpar memória temporária do raster bruto
  rm(dados, raster_cortado); gc()
  
  # Diminuindo a resolução a fim de otimizar o código
  raster_agregado <- aggregate(raster_mascarado, fact = 4, fun = modal)
  raster_df <- as.data.frame(raster_agregado[[1]], xy = TRUE)
  names(raster_df) <- c("x", "y", "valor")
  
  # Limpar o raster_mascarado e agregado da memória
  rm(raster_mascarado, raster_agregado); gc()
  
  # CLASSIFICAÇÃO
  raster_df$classe <- ifelse(is.na(raster_df$valor), "Sem Informação",
                             ifelse(raster_df$valor %in% c(22,23,24,30,25), "Sem vegetação",
                                    ifelse(raster_df$valor %in% c(26,33,31), "Corpo de água",
                                           ifelse(raster_df$valor %in% c(1,3,4,5,6,49,10,11,12,32,29,50), "Vegetação", "Agropecuária"))))
  
  # Transformar em 'factor' para garantir que fiquem na ordem certa na legenda
  raster_df$classe <- factor(raster_df$classe,
                             levels = c("Corpo de água", "Sem vegetação",
                                        "Vegetação", "Agropecuária", "Sem Informação"))
  
  # Criar mapa
  mapa <- ggplot() +
    geom_raster(data = raster_df, aes(x = x, y = y, fill = classe)) +
    scale_fill_manual(
      values = c(
        "Corpo de água"  = "blue",
        "Sem vegetação"  = "brown",
        "Vegetação"      = "green",
        "Sem Informação" = "white",
        "Agropecuária"   = "#f1c131"
      )
    ) +
    geom_sf(data = municipios_sf, fill = NA, color = "black", linewidth = 0.5) +
    theme_minimal() +
    annotation_north_arrow() +
    annotation_scale(location = "br") +
    labs(
      x    = "Longitude",
      y    = "Latitude",
      fill = "Uso e Corbetura do Solo"
    ) +
    ggtitle(paste("Uso e Corbetura do Solo no Nordeste ", ano))
  
  # Salvar o mapa gerado na pasta 'mapas_prontos'
  nome_arquivo <- paste0("mapas_prontos_nordeste/mapas_prontos_nordeste", ano, ".png")
  ggsave(filename = nome_arquivo, plot = mapa, width = 16, height = 10, dpi = 450, bg = "white")
  
  message("Mapa de ", ano, " salvo com sucesso!")
  
  # -----------------------------------------------------------------------
  # LIMPEZA DE ARQUIVOS TEMPORÁRIOS AO FINAL DE CADA ITERAÇÃO
  # -----------------------------------------------------------------------
  
  # 1. Remove objetos R remanescentes e força coleta de lixo
  rm(raster_df, mapa, nome_arquivo); gc()
  
  # 2. Identifica e deleta apenas os arquivos temporários criados NESTA iteração
  temps_depois <- list.files(tempdir(), full.names = TRUE)
  temps_novos  <- setdiff(temps_depois, temps_antes)
  
  if (length(temps_novos) > 0) {
    deletados <- file.remove(temps_novos)
    message(
      "  → ", sum(deletados), " arquivo(s) temporário(s) deletado(s) | ",
      sum(!deletados), " não pôde(ram) ser removido(s)."
    )
  } else {
    message("  → Nenhum arquivo temporário novo encontrado.")
  }
  
  # 3. Limpa também os arquivos temporários internos do pacote raster
  showTmpFiles()
  removeTmpFiles(h = 0)
  
  message("  ✓ Ano ", ano, " concluído.\n")
}

message("=== Todos os mapas foram processados! ===")