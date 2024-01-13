---
layout: page
title: Software
menu: main
permalink: /software/
---
<h3>R Packages for Advanced Statistical Analysis</h3>

<p>Explore these R packages designed to address specific challenges in spatial data processing, high-dimensional
    modeling, and diagnostics of binary classification.</p>


<div class="list-group">
    <div class="list-group-item">
        <h4 class="list-group-item-heading"><a href="https://egpivo.github.io/SpatPCA/">SpatPCA</a></h4>
        <p class="list-group-item-text"> Simplify spatial data analysis with the `SpatPCA` package. This tool excels
            in regularized principal component analysis, enabling the identification of dominant patterns
            (eigenfunctions) characterized by smoothness and localization. It also facilitates spatial prediction
            (Kriging) for new locations, accommodating both regularly and irregularly spaced data. The package
            leverages the efficient alternating direction method of multipliers (ADMM) algorithm.
        </p>
        <ul class="list-inline">
            <li><i class="fab fa-github fa-lg"></i> <a href="https://github.com/egpivo/SpatPCA">GitHub</a></li>
            <li><a href="https://cran.rstudio.com/web/packages/SpatPCA"><img
                    src="http://www.r-pkg.org/badges/version/SpatPCA"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/SpatPCA"><img
                    src="http://cranlogs.r-pkg.org/badges/SpatPCA"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/SpatPCA"><img
                    src="https://cranlogs.r-pkg.org/badges/grand-total/SpatPCA"/></a></li>
            <li><a href="https://codecov.io/github/egpivo/SpatpCA?branch=master"><img
                    src="https://img.shields.io/codecov/c/github/egpivo/SpatPCA/master.svg"/></a></li>
            <li><a href="https://doi.org/10.1080/10618600.2016.1157483"><img
                    src="https://img.shields.io/badge/JCGS-10.18637%2F10618600.2016.1157483-brightgreen"/></a></li>
        </ul>
    </div>
    <div class="list-group-item">
        <h4 class="list-group-item-heading"><a href="https://egpivo.github.io/SpatMCA/">SpatMCA</a></h4>
        <p class="list-group-item-text"> Delve into regularized maximum covariance analysis with the SpatMCA R
            package. This tool excels in identifying smooth and localized patterns that reveal the influence of
            one spatial process on another. Like SpatPCA, it accommodates both regularly and irregularly spaced
            data and employs the efficient ADMM algorithm.
        </p>
        <ul class="list-inline">
            <li><i class="fab fa-github fa-lg"></i> <a href="https://github.com/egpivo/SpatMCA">GitHub</a></li>
            <li><a href="https://cran.rstudio.com/web/packages/SpatMCA"><img
                    src="http://www.r-pkg.org/badges/version/SpatMCA"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/SpatMCA"><img
                    src="http://cranlogs.r-pkg.org/badges/SpatMCA"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/SpatMCA"><img
                    src="https://cranlogs.r-pkg.org/badges/grand-total/SpatMCA"/></a></li>
            <li><a href="https://codecov.io/github/egpivo/SpatMCA?branch=master"><img
                    src="https://img.shields.io/codecov/c/github/egpivo/SpatMCA/master.svg"/></a></li>
            <li><a href="https://doi.org/10.1002/env.2481"><img
                    src="https://img.shields.io/badge/Environmetrics-10.1002%2Fenv.2481-brightgreen"/></a></li>
        </ul>
    </div>
    <div class="list-group-item">
        <h4 class="list-group-item-heading"><a href="https://egpivo.github.io/autoFRK/">autoFRK</a></h4>
        <p class="list-group-item-text"> The `autoFRK`, R package, built on RcppEigen, introduces automatic
            fixed-rank
            kriging for spatial data. It stands out for its capability to handle irregularly distributed data
            points
            using a set of basis functions with multi-resolution characteristics, intelligently ordered based on
            their
            resolutions.
        </p>
        <ul class="list-inline">
            <li><i class="fab fa-github fa-lg"></i> <a href="https://github.com/egpivo/autoFRK">GitHub</a></li>
            <li><a href="https://cran.rstudio.com/web/packages/autoFRK"><img
                    src="http://www.r-pkg.org/badges/version/autoFRK"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/autoFRK"><img
                    src="http://cranlogs.r-pkg.org/badges/autoFRK"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/autoFRK"><img
                    src="https://cranlogs.r-pkg.org/badges/grand-total/autoFRK"/></a></li>
            <li><a href="https://codecov.io/github/egpivo/autoFRK?branch=master"><img
                    src="https://img.shields.io/codecov/c/github/egpivo/autoFRK/master.svg"/></a></li>
        </ul>
    </div>
    <div class="list-group-item">
        <h4 class="list-group-item-heading"><a href="https://boshiangke.github.io/InfluenceAUC/">influenceAUC</a></h4>
        <p class="list-group-item-text"> Specialized in binary classification model diagnostics, the
            influenceAUC package is essential for identifying influential observations. It provides crucial
            visualization tools to enhance the understanding of model performance and diagnostic insights.
        </p>
        <br/>
        <ul class="list-inline">
            <li><i class="fab fa-github fa-lg"></i> <a href="https://github.com/BoShiangKe/influenceAUC">GitHub</a>
            </li>
            <li><a href="https://cran.rstudio.com/web/packages/influenceAUC"><img
                    src="http://www.r-pkg.org/badges/version/influenceAUC"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/influenceAUC"><img
                    src="http://cranlogs.r-pkg.org/badges/influenceAUC"/></a></li>
            <li><a href="https://cran.rstudio.com/web/packages/influenceAUC"><img
                    src="https://cranlogs.r-pkg.org/badges/grand-total/influenceAUC"/></a></li>
        </ul>
    </div>
    <div class="list-group-item">
        <h4 class="list-group-item-heading"><a href="https://egpivo.github.io/QuantRegGLasso/">QuantRegGLasso</a></h4>
        <p class="list-group-item-text">
            Designed to tackle quantile regression challenges through adaptively weighted group Lasso procedures, the
            QuantRegGLasso package excels in concurrently selecting variables and identifying structures for varying
            coefficient quantile regression models. Additionally, it performs effectively in the context of additive
            quantile regression models, particularly when dealing with ultra-high dimensional covariates.
        </p>
        <br/>
        <ul class="list-inline">
            <li><i class="fab fa-github fa-lg"></i> <a href="https://github.com/egpivo/QuantRegGLasso">GitHub</a>
            </li>
            <li><a href="https://github.com/egpivo/QuantRegGLasso/actions"><img
                    src="https://github.com/egpivo/QuantRegGLasso/workflows/R-CMD-check/badge.svg"/></a></li>
            <li><a href="https://app.codecov.io/github/egpivo/QuantRegGLasso?branch=master"><img
                    src="https://img.shields.io/codecov/c/github/egpivo/QuantRegGLasso/master.svg"/></a></li>
        </ul>
    </div>
</div>


<h3>Python Implementations</h3>
<p>Explore the following Python applications showcasing a range of technologies and frameworks.</p>


<div class="list-group">
    <div class="list-group-item">
        <h4 class="list-group-item-heading"><a href="https://egpivo.com/chatbot">LLM Chatbot</a></h4>
        <p class="list-group-item-text">
            Unleash the potential of conversational AI with the LLM Chatbot Framework.This Python framework, powered by LangChain Agent, seamlessly integrates advanced text-to-speech and speech-to-text models from Hugging Face. Craft dynamic chatbots with voice translation capabilities effortlessly.
        </p>
        <br>
        <div class="software-ref">
            <strong>Software References:</strong>
            <ul class="list-inline">
                <li><i class="fab fa-github fa-lg"></i> <a href="https://github.com/egpivo/chatbot">GitHub</a></li>
                <li><i class="fas fa-eye fa-lg"></i> <a href="https://egpivo.com/chatbot/">Demo</a></li>
            </ul>
        </div>
        <div class="build-deployment">
            <strong>Build and Deployment:</strong>
            <ul class="list-inline">
                <li><a href="https://github.com/egpivo/chatbot/actions"><img
                        src="https://github.com/egpivo/chatbot/workflows/CI/badge.svg"/></a></li>
                <li><a href="https://codecov.io/gh/egpivo/chatbot"><img
                        src="https://codecov.io/gh/egpivo/chatbot/branch/main/graph/badge.svg"/></a></li>
                <li><a href="https://hub.docker.com/r/egpivo/chatbot/tags"><img
                        src="https://img.shields.io/docker/pulls/egpivo/chatbot"/></a></li>
                <li><a href="https://hub.docker.com/r/egpivo/chatbot/tags"><img
                        src="https://img.shields.io/docker/image-size/egpivo/chatbot"/></a></li>
                <li><a href="https://hub.docker.com/r/egpivo/chatbot/tags"><img
                        src="https://img.shields.io/docker/v/egpivo/chatbot/latest"/></a></li>
            </ul>
        </div>
        <div class="tech-stack">
            <strong>Tech Stack:</strong>
            <ul class="list-inline">
                <li><a href="#"><img src="https://img.shields.io/badge/openai-black?style=flat-square&logo=openai"/></a>
                </li>
                <li><a href="#"><img
                        src="https://img.shields.io/badge/Hugging_Face-black?style=flat-square&logo=hugging%20face"/></a>
                </li>
                <li><a href="#"><img
                        src="https://img.shields.io/badge/LangChain-007ACC?style=flat-square&logo=langchain&logoColor=black"/></a>
                </li>
                <li><a href="#"><img
                        src="https://img.shields.io/badge/PyTorch-black?style=flat-square&logo=pytorch"/></a></li>
                <li><a href="#"><img
                        src="https://img.shields.io/badge/fastapi-black?style=flat-square&logo=fastapi"/></a></li>
                <li><a href="#"><img
                        src="https://img.shields.io/badge/bentoml-black?style=flat-square&logo=bentoml"/></a></li>
                <li><a href="#"><img
                        src="https://img.shields.io/badge/Gradio-4A4A4A?style=flat-square&logo=gradio&logoColor=black"/></a>
                </li>
                <li><a href="#"><img src="https://img.shields.io/badge/docker-black?style=flat-square&logo=docker"/></a>
                </li>
                <li><a href="#"><img
                        src="https://img.shields.io/badge/AlibabaCloud-orange?logo=alibaba-cloud&color=black"/></a></li>
            </ul>
        </div>
    </div>
</div>