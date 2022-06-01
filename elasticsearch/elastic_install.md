엘라스틱 서치 설치방법
엘라스틱 서치를 aistage에서 사용하기 위해선 최신 버전인 8 버전을 사용하면 안됩니다.
또한 노리 형태소 분석기를 사용하기 위해선 엘라스틱 서치 6.6 버전 이상을 사용해야 됩니다.
만약 군집화 기능을 사용한다면 carrot2를 사용할 수 있기 때문에, 설치는 7.14.1 버전을 기준으로 진행하겠습니다.


1. 엘라스틱 서치 설치
https://www.elastic.co/guide/en/elasticsearch/reference/7.14/targz.html 를 참고하여 다음 명령어를 수행합니다.
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.14.1-linux-x86_64.tar.gz
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.14.1-linux-x86_64.tar.gz.sha512
shasum -a 512 -c elasticsearch-7.14.1-linux-x86_64.tar.gz.sha512 
tar -xzf elasticsearch-7.14.1-linux-x86_64.tar.gz
cd elasticsearch-7.14.1/


2. 노리 분석기 설치
터미널 위치가 elasticsearch-7.14.1에 있는 것을 확인한 후 다음 명령어를 실행합니다.
bin/elasticsearch-plugin install analysis-nori


3. Carrot2 설치 (옵션)
위와 같은 위치에 터미널이 있는지 확인하고 다음 명령어를 실행합니다.
bin/elasticsearch-plugin install org.carrot2:elasticsearch-carrot2:7.14.1


4. 유저 생성
aistage 서버의 root는 권한이 부족하여 elasticsearch 실행을 할 수 없습니다. 따라서 새로 유저를 생성하여 실행해야 합니다. aistage 게시물을 참고하면 됩니다.

유저 설정 방법


    $ passwd root
    (설정한 root 계정의 비밀번호 입력)

    $ useradd [만드려는_계정_이름]
    (계정 추가)
    ex) useradd kiwon
    
    $ chown -R [만든_계정_이름]:[만든_계정_이름] [Elasticsearch_경로]
    (해당 계정으로 Elasticsearch 실행 권한 주기 마지막에는 Elasticsearch 경로를 작성하면 됩니다.)
    ex) chown -R kiwon:kiwon /opt/ml/elasticsearch-7.14.1
   
    $ su 만든_계정_이름
    (계정전환)
    ex) su kiwon


5) 엘라스틱 서치 실행
su 계정이름으로 유저를 변경한 이후
터미널 위치가 elasticsearch-7.14.1에 있는 것을 확인한 후 다음 명령어를 실행합니다.
bin/elasticsearch
만약 자바와 관련해서 오류가 발생하면 6번을 진행합니다.


6) 자바 오류 수정 (옵션)
만약 자바 설정과 관련해서 오류가 발생하면 다음과 같이 진행합니다. 
aistage 토론 게시판 참고


      $apt-get install openjdk-11-jdk

      $java -version
      (11 버전이 확인되면 ok)

      $vi /etc/profile 실행

      $export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/jre

      $export PATH=$PATH:$JAVA_HOME/bin
      (마지막 줄에 추가)

      $source /etc/profile


7) 코드실행
깃헙에 올라간 elastic.ipynb를 실행한 다음 오류가 생기면 알려주세요!
