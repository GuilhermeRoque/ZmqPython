
### Relaório Técnico

#### ZMQ
- Abstração da programação direta com sockets;
- Sem necessidade de uma persistência visto que o programa é feito para um cluster;
- Padrão **publish & subscribe** para mensagens globais de controle utilizadas;
-- Ex: Comando para inicar quebra de arquivo, comando para parar quebra de arquivo;
- Padrão **request & reply** para mensagens únicas entre mestre e escravo;
-- Ex: Anunciamento na rede, envio de status, envio de notificação, envio de configuração;

#### Funcionamento
