<!-- Readme for Genetic Screening Web Automation by Trent Neilson -->
<a name="readme-top"></a>

[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- <a href="https://github.com/secretx51/Genetic-Screening-Web-Automation">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

<h3 align="center">Genetic Screening Web Automation</h3>

  <p align="center">
    Accelerate your genetic horizontal screening.
    <br />
    <a href="https://github.com/secretx51/Genetic-Screening-Web-Automation"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/secretx51/Genetic-Screening-Web-Automation/issues">Report Bug</a>
    ·
    <a href="https://github.com/secretx51/Genetic-Screening-Web-Automation/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#gepia">Gepia</a></li>
        <li><a href="#linkedomics">LinkedOmics</a></li>
        <li><a href="#ncbi">NCBI</a></li>
        <li><a href="#tide">Tide</a></li>
        <li><a href="#timer">Timer</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Modern bioinformatic genetic screening requires the use of many online web tools for the analysis of genes. This project includes the following web tools: Gepia, LinkedOmics, Tide and Timer. This project allows for fast horizontal analysis, via automating the input of genes into these online web-tools with python selenium.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To use this project, install python 3.10 with your preferred package manager. Clone the repo. Install the required packaged from requirements.txt. Detailed instructions found below in prerequisites and installation.

### Prerequisites

Install python 3.10 with your preferred package manager. <br />
Instructions to install conda found [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). <br />
Example install python 3.10 with conda below:
  ```sh
  conda update conda
  conda create --name py10 python=3.10 
  WINDOWS: activate py10
  LINUX, macOS: source activate py10
  ```

### Installation
1. Install git - WINDOWS only
   ```sh
   winget install --id Git.Git -e --source winget
   ```
2. Clone the repo to directory of your choice
   ```sh
   git clone https://github.com/secretx51/Genetic-Screening-Web-Automation.git
   ```
3. Install required python packages using pip at cloned directory.
   ```sh
   pip install -r requirements.txt
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

Every tool has a corresponding directory that contains the python file to run and text file that you should store you comma delineated genes for the tool to run in. For specific guides and further descriptions of each tool see below. <br />
IMPORTANT: Before running each tool check the main python file and update any directory constants. <br /><br />
General guide to running each tool:
1. Update corresponding toolnameGenes.txt file with a comma separated list of the genes you want the tools to conduct analysis on. <br />
2. Go to the main python file and update any directory constants.
3. CD to the directory of the tool you want to run
   ```sh
   cd toolname/
   ```
4. Run the main python file
   ```sh
   python toolnameMain.py
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>
  

### Gepia

Gets survival data from Gepia for all the comma separated genes in 'gepiaGenes.txt'. Gepia is the only one of the online web automation tools that doesn't use selenium to parse webpages. This is because Gepia has a public python API that the program uses to generated the data. It generates the output in the form of pdf files that have an image of the survival plot. It then extracts all the text from the pdf files and filters for HR(high) and logranks which it stores in a csv alongside the respective gene name. <br />
  ```sh
  Gets Logrank and HR(high) from Gepia survival data
  options:
    -h, --help            show this help message and exit

    -o, --outdir          Directory to where pdf graphs should be stored. 
                          Default is: /python-file-directory/output

    -c , --cancer         Cancer type to run Gepia on. 
                          Default is: 'OV'.
                          Choices are: ACC,BLCA,BRCA,CESC,CHOL,COAD,DLBC,ESCA,GBM,HNSC,KICH,KIRC,KIRP,
                          LAML,LGG,LIHC,LUAD,LUSC,MESO,OV,PAAD,PCPG,PRAD,READ,SARC,SKCM,STAD,TGCT,THCA,
                          THYM,UCEC,UCS
  ```
Example to run python script with directory changed and BRCA cancer type:
  ```sh
  python tideMain.py -o /Users/myUser/Developer/gepia/results -c BRCA
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### LinkedOmics

Does a pearson corelation test using rna seq data as search and target dataset in the TCGA_OV database for each comma separated genes in 'linkedomicsGenes.txt'. Conducts a linked-interpreter analysis using Gene Set Enrichment Analysis (GSEA) using the gene ontology enrichment analysis, ranking with FDR, min samples of 3 and 500 simulations. Uses selenium web automation to enter all parameters into the website and downloads the table from page source. The tool then filters this table for the FDR and P-values of immunological pathways determined by gene ontology terms. <br />
To change the gene ontology terms do the follow:
1. Update the 'GO_search_terms.txt' do include a list of terms you want to get gene ontology tags for.
2. CD to the Gene Ontology directory
   ```sh
   cd Gepia/GeneOntology/
   ```
3. Run the main python file
   ```sh
   python getGoTerms.py
   ```
The terms will then be added to the output_GO_terms.txt file that LinkedOmics uses to filter for desired pathways.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### NCBI

This library contains 2 tools 'filterGenome.py' and 'geneSplitter.py'. filterGenome.py is designed to find genes from the human genome that you would like to run further testing on through the other tools. filterGenome.py does not search  the web through selenium or Gepia API request, instead it uses data from the 'NCBI/gene/gene_info/Homo_sapiens'.gene_info. This file is updated daily by NCBI the current version in use is from 05/07/2023. To use filter genome enter the prefixes of genes you desire into the 'genomeSearchTerms.txt' file in a comma delineated format. For example entering MIR,LET into the format would return all the microRNA genes from the human genome. <br /><br />

geneSplitter.py is located in /vm_tools and is designed to split a comma separated list of genes into multiple files. It is reserved for advanced users only that would like to run multiple of instances of selenium at once through containers/vms. To use it you must edit the python file with input directory of file, output directory for split files and project name to names the files.
<br />
formatMicroRNA.py is also locate in /vm_tools and is designed to format miRNA gene names as to work better with most miRNA databases including linkedOmics. Only used this miRNA gene names and nothing else. To use it you must edit the python file with input directory of file and output directory for the formatted gene names.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Tide

Downloads the expression and exclusion tables from the Tide query gene tool using python selenium. It then filters these tools for ovarian and ovary patients and subsets for the datasets of interest. It reports the T_Dysfunction value for each dataset. <br />
The default datasets are: <br />
Ovarian expression: "GSE26712@PRECOG", "GSE13876@PRECOG", "GSE3149@PRECOG", "GSE9899@PRECOG", "GSE17260@PRECOG" and
TCGA that is split into arbitrary "TCGA1" and "TCGA2" <br />
Ovary Expression: "GSE17260", "GSE49997", "GSE32062", "GSE26712" <br />
Exclusion: 'CAF FAP', 'MDSC', 'TAM M2' <br />
These datasets can be changed by entering the exact name of desired dataset in a comma separated fashion into the text file 'tideCohorts.txt'.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Timer
Enters comma separated list of genes into 'timerGenes.txt'. The genes from this file are entered into Timer 2.0 gene section which allows for the correlation and expression of CD8+ T cell immune infiltration level in ovarian cancer.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Classify Tide and Gepia
- [x] Restructure folder directory and file naming
- [x] Remove need for user to edit files by auto-directory detection
- [ ] Refactor LinkedOmics and Timer
- [ ] Allow to be used with other cancer types apart from ovarian
    - [ ] Allow alternate parameter input by user
    - [ ] Implement Parser
- [ ] Dockerise
    - [ ] Potential to implement simple web UI

See the [open issues](https://github.com/secretx51/Genetic-Screening-Web-Automation/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Trent Neilson - trent.neilson99@gmail.com

Project Link: [https://github.com/secretx51/Genetic-Screening-Web-Automation](https://github.com/secretx51/Genetic-Screening-Web-Automation)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Gepia](http://gepia2.cancer-pku.cn/#index)
* [LinkedOmics](https://linkedomics.org/)
* [NCBI](https://www.ncbi.nlm.nih.gov/gene)
* [Tide](http://tide.dfci.harvard.edu/)
* [Timer](http://timer.cistrome.org/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[forks-shield]: https://img.shields.io/github/forks/secretx51/Genetic-Screening-Web-Automation.svg?style=for-the-badge
[forks-url]: https://github.com/secretx51/Genetic-Screening-Web-Automation/network/members
[stars-shield]: https://img.shields.io/github/stars/secretx51/Genetic-Screening-Web-Automation.svg?style=for-the-badge
[stars-url]: https://github.com/secretx51/Genetic-Screening-Web-Automation/stargazers
[issues-shield]: https://img.shields.io/github/issues/secretx51/Genetic-Screening-Web-Automation.svg?style=for-the-badge
[issues-url]: https://github.com/secretx51/Genetic-Screening-Web-Automation/issues
[license-shield]: https://img.shields.io/github/license/secretx51/Genetic-Screening-Web-Automation.svg?style=for-the-badge
[license-url]: https://github.com/secretx51/Genetic-Screening-Web-Automation/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/trent-neilson
