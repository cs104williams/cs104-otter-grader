
install.packages(c(
    "gert",
    "usethis",
    "testthat",
    "startup"
), dependencies=TRUE, repos="http://cran.us.r-project.org")

install.packages("stringi", configure.args="--configure-args='--disable-pkg-config --with-extra-cxxflags="--std=c++11" --disable-cxx11'", repos="http://cran.us.r-project.org")
