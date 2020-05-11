$(document).ready(function () {
    //set defaults value varibles and states
    var currentSrId = -1;
    var currentProjectId = -1;
    $('#ProjectList').hide();
    $('#ProjectContent').hide();
    $('#commentsContent').hide();
    $('#srList').hide();
    //save data as js object
    // tu trzeba wyciągnąć js'na z bazy
    var stringJson = {
        "result": 1,
        "data": [{
            "id": 1,
            "name": "Środowisko nr 1",
            "projects": [{"id": 1, "name": "projektnr1"}, {"id": 2, "name": "projektnr2"}, {
                "id": 3,
                "name": "projektnr3"
            }, {"id": 4, "name": "projektnr14"}]
        }, {
            "id": 2,
            "name": "Środowisko nr 2",
            "projects": [{"id": 5, "name": "projektnr5"}, {"id": 6, "name": "projektnr6"}, {
                "id": 7,
                "name": "projektnr7"
            }, {"id": 8, "name": "projektnr8"}]
        }, {
            "id": 3,
            "name": "Środowisko nr 3",
            "projects": [{"id": 9, "name": "projektnr9"}, {"id": 10, "name": "projektnr10"}, {
                "id": 11,
                "name": "projektnr11"
            }, {"id": 12, "name": "projektnr12"}]
        }, {
            "id": 4,
            "name": "Środowisko nr 4",
            "projects": [{"id": 13, "name": "projektnr13"}, {"id": 14, "name": "projektnr14"}, {
                "id": 15,
                "name": "projektnr15"
            }, {"id": 16, "name": "projektnr16"}]
        }, {
            "id": 5,
            "name": "Środowisko nr 5",
            "projects": [{"id": 17, "name": "projektnr17"}, {"id": 18, "name": "projektnr18"}, {
                "id": 19,
                "name": "projektnr19"
            }, {"id": 19, "name": "projektnr19"}]
        }, {
            "id": 6,
            "name": "Środowisko nr 6",
            "projects": [{"id": 20, "name": "projektnr20"}, {"id": 21, "name": "projektnr21"}, {
                "id": 22,
                "name": "projektnr22"
            }, {"id": 23, "name": "projektnr23"}]
        }]
    };
    //var obj = JSON.parse(stringJson);
    var obj=stringJson;
    //generate List of Enviroiments

    //funkcja zczytująca parametry geta
    $.urlParam = function (name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results == null) {
            return null;
        }
        return decodeURI(results[1]) || 0;
    }
    if ($.urlParam('sr') != null) {

        $.each(obj['data'], function (index, element) {
            if (element['id'] == $.urlParam('sr')) {
                console.log('ok');
                loadListProjects(index);
            }
        });
    } else if ($.urlParam('pr') != null) {
        $.each(obj['data'], function (indexSr,elementSr) {
            $.each(obj['data'][indexSr]['projects'],function (index,element) {
                if(element['id']==$.urlParam('pr')){
                    currentSrId=indexSr;
                     loadListProjects(currentSrId);
                     loadProject(index);
                }
            })

        });
    } else
        $('#srList').fadeIn(500);
    //wczytanie środowisk
    $.each(obj.data, function (id) {
        var nameSr = obj.data[id]['name'];
        var srString = "<div class='col-lg-4  col-sm-12 text-center envi' data-sr-id='" + id + "'><div   class='w-100 h-100 rounded-pill  p-5'><h3>" + nameSr + "</h3></div></div>"
        $('#srList').append(srString);
    })
    // event wybierający srodowisko
    $('.envi').each(function () {
        $(this).on('click', function () {
            loadListProjects($(this).attr('data-sr-id'))
        });
    });


    //załadowanie projektów po wybraniu
    function loadListProjects(idSr) {
        projects = obj.data[idSr]['projects'];
        currentSrId = idSr;
        breadcrumb();
        var projectsStr = "<div class='row projectsRow  text-center'>";
        $.each(projects, function (id_pro) {
            projectsStr += "<div class='col-lg-4 ProjectItemx' data-project-id='" + id_pro + "'><div class='  w-100 h-100 rounded-pill  p-5'><h4>" + projects[id_pro]['name'] + "</h4></div></div>";
        });
        projectsStr += "</div>";
        $('#ProjectList').html(projectsStr);
        $('#srList').hide();
        $('#ProjectList').hide();
        $('#ProjectList').fadeIn(500);
        loadEventProject();
    }


    //breadcrumb actions
    function breadcrumb() {
        if (currentSrId === -1 && currentProjectId === -1) {
            str = " <li class=\"breadcrumb-item active\"><button id='ToHome' class='btn'>Home</button></li>";
            $('#breadcrumb').html(str);
        } else if (currentProjectId === -1) {
            var nameSr = obj.data[currentSrId]['name'];
            str = " <li class=\"breadcrumb-item \"><button id='ToHome' class='btn'>Home</button></li>" +
                "<li class=\"breadcrumb-item active\"><button  id='ToSr'  class='btn' href=\"#\">" + nameSr + "</button></li>";
            $('#breadcrumb').html(str);
        } else {
            var nameSr = obj.data[currentSrId]['name'];
            var namePr = obj.data[currentSrId]['projects'][currentProjectId]['name'];
            str = " <li class=\"breadcrumb-item \"><button id='ToHome' class='btn'>Home</button></li>" +
                "<li class=\"breadcrumb-item \"><button id='ToSr' class='btn'>" + nameSr + "</button></li>" +
                "<li class=\"breadcrumb-item active\"><button class='btn'>" + namePr + "</button></li>";
            $('#breadcrumb').html(str);
        }
        $('#ToHome').on('click', function () {
            $('#srList').fadeIn(500);
            $('#ProjectList').hide();
            $('#ProjectContent').hide();
             $('#ProjectContent').addClass('h-0');
            currentSrId = -1;
            currentProjectId = -1;
            breadcrumb();
        });
             $('#ToSr').on('click', function () {
             $('#srList').hide();
             $('#ProjectContent').hide();
             $('#ProjectContent').addClass('h-0');
            $('#ProjectList').fadeIn(500);

            currentProjectId = -1;
            breadcrumb();
        });
    }

    breadcrumb();

    //show project
    function loadEventProject() {
        $('.ProjectItemx').each(function () {
            $(this).on('click', function () {
               loadProject($(this).attr('data-project-id'));

            });
        });
    }
    function loadProject(dataProjectId) {
              project = obj.data[currentSrId]['projects'][dataProjectId];
                console.log(project);
                currentProjectId = dataProjectId;
                breadcrumb();
                $('#srList').hide();
                $('#ProjectList').hide();


                //ładowanie z api projektu
                // dla id obiektu project['id'] z ajaxa załaduj do proObj
                proObj = {
                    "result": 1,
                    "data": {
                        "id": 1,
                        "name": "Projekt 1234",
                        "status": "Status Nowy",
                        "category": "Kategoria1",
                        "content": "jakas tam zawartosc projektu",
                        "comments": [
                            {
                                "commenter": "Mateusz Wróblewski",
                                "title": "Tytuł komentarza 1",
                                "content": "Tu jest to i to źle",
                                "reaction": "cos",
                                "date": "2020-03-03"
                            }
                            ,
                            {
                                "commenter": "Mateusz Wróblewski 2",
                                "title": "Tytuł komentarza 2",
                                "content": "Tu jest to i to źle2",
                                "reaction": "co2s",
                                "date": "2020-03-05"
                            }
                        ]

                    }
                };
                projectContent(proObj);
                $('#ProjectContent').addClass('h-0');

                $('#ProjectContent').show();
                $('#ProjectContent').removeClass('h-0', 1000);
    }
    function projectContent(proObj) {
        $('#projTitle').html(proObj['data']['name']);
        $('#projCategory').html(proObj['data']['category']);
        $('#projStatus').html(proObj['data']['status']);
        $('#projContent').html(proObj['data']['content']);
        console.log(proObj['data']['comments']);
        $('#commentsContentDiv').html("");
        $.each(proObj['data']['comments'], function (id_projectArray) {
            console.log(proObj['data']['comments'][id_projectArray]);
            var com = proObj['data']['comments'][id_projectArray];
            $('#commentsContentDiv').append(generateComment(com));
        });
        $('#commentsContent').hide();
        $('#commentsContent').addClass('h-0');

    }

    function generateComment(com) {
        stringComment = " <div class=\"col-12\" style='padding-top: 1rem'>\n" +
            "                       <div style=\"\">\n" +
            "                    <span style=\"height: 2rem;font-size: 1.1rem ;\">\n" +
            "                             <b><img src=\"/static/pznsi/images/user.ico\" class=\"img-comment\" ></b>\n" +
            "                        <b>" + com['commenter'] + "</b>\n" +
            "                        <span class=\"dateCom\">" + com['date'] + "</span>\n" +
            "                    </span>\n" +
            "                       <div class=\"col-12 flex-lg-wrap\">\n" +
            "                           " + com['content'] + "" +
            "                       </div>\n" +
            "                         </div>\n" +
            "                    </div>";
        return stringComment
    }
    //eventy
    $('#btnKom').on('click', function () {

                $('#commentsContent').toggle(300);
                $('#commentsContent').toggleClass('h-0', 400);
        });
    $('#addComment').on('click', function () {
        var comment = $('#newComment').val();

        if (comment != '') {
            var com = {
                "commenter": "Mateusz Wróblewski",
                "date": "2020-03-30",
                "content": comment
            }
            $('#commentsContentDiv').append(generateComment(com));
            $('#newComment').val("");
        }
    });


});