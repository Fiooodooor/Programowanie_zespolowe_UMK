var FileToUploadAttachment = ""; //dane formularza plików
var dataCommentAttachment = []; //dane dotyczące komentarzy i zalacznikow
var votes = []; //dane dotyczace głosów
var currentUser = '{{ user.id }}';
//tryby pracy 1- strona główna (Ostatnie projekty) oraz lista środowisk
//tryb pracy 2 przegląd  projektów z wybranego środowiska
//tryb pracy 3 Edycja środowiska
//tryb pracy 4 Edycja uprawnień środowiskaEventProjectClick
//tryb pracy 5 widok projektu
//tryb pracy 6 edycja projektu
//tryb pracy 7 uprawnienia projektu
var trybPracy = 1;
var WybraneSrodowisko = -1;
var selectedEnvi = "";
var pageLoad = 1;
var search = 0;
var stopReadPage = 0;
var keyword = "";
var selectedProject = 0;
var selectedProjectName = "";
var backgroundurl = "";
var repoItem = 0;
var repoItemUrl = "";
var repoItemName = "";
var selectedFile = "";
var locale = {
    OK: 'Potwierdź',
    CONFIRM: 'Potwierdź',
    CANCEL: 'Anuluj'
};
bootbox.addLocale('custom', locale);

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// funkcje srodowisk
function EventEnviClick() {
    //po wcisnieciu przycisku edytuj przechodzi do edycji envi
    $(".editEnviButton").on('click', function (event) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        WybraneSrodowisko = $(this).attr('data-envi-id');
        selectedEnvi = $(this).attr('data-envi-name');
        backgroundurl = $(this).attr('data-background');
        trybPracy = 3;
        ZmianaTrybuPracy();
    });
    //wejście w uprawnienia aplikacji
    $(".permEnviButton").on('click', function (event) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        WybraneSrodowisko = $(this).attr('data-envi-id');
        selectedEnvi = $(this).attr('data-envi-name');
        backgroundurl = $(this).attr('data-background');
        trybPracy = 4;
        ZmianaTrybuPracy();
    });
    $(".removeEnviButton").on('click', function (event) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        e = this;
        selectedEnviNum = $(this).attr('data-envi-id');
        bootbox.confirm("Czy napewno chcesz usunąć Środowisko i Projekty ?", function (result) {
            if (result) {
                $('#loadingSpinner').show();
                $.ajax({
                    url: '/api/environments/' + selectedEnviNum + '/',
                    type: 'delete',
                    success: function (result) {
                        $('#loadingSpinner').hide();
                        $(e).parent().parent().parent().fadeOut(100);
                        LoadLastProjectList();
                        ZmianaTrybuPracy();
                    }
                }).fail(function () {
                    $('#loadingSpinner').hide();
                    bootbox.alert({
                        message: "Wystąpił błąd",
                        centerVertical: true,
                    });
                });
            }
        });
    });
    //po kliknięciu w środowisko wchodzi do listy projektów
    $(".EnviListElement").on('click', function (event) {
        backgroundurl = "";
        WybraneSrodowisko = $(this).attr('data-envi-id');
        selectedEnvi = $(this).attr('data-envi-name');
        backgroundurl = $(this).attr('data-background');
        event.stopPropagation();
        event.stopImmediatePropagation();
        trybPracy = 2;
        ZmianaTrybuPracy();

    });
}


// funkcje workspace !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
function setDefaultWorkspace() {
    $('.repoItem').on('click', function () {
        repoItemUrl = $(this).attr('data-value-url');
        repoItem = $(this).attr('data-id-repofile');
        repoItemName = $(this).attr('data-id-reponame');
        $('#addItemRepoToProject').hide();
        $('#downloadFileRepo').attr('href', repoItemUrl);
        if (trybPracy == 5) $('#addItemRepoToProject').show();
        $('#repoactionModal').modal();
    });
    $('#addItemRepoToProject').on('click', function () {
        $('#loadingSpinner').show();
        $.post('/api/repository/' + repoItem + '/add_to_project/', {'project_id': selectedProject}, function () {
            dataLoadProject();
            $('#repoactionModal').modal('hide');
            $('#loadingSpinner').hide();
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        })
    });
    $('#addFileRepoDiv > span').on('click', function () {
        $('#fileBackgroundRepo').click();
    });
    $('#addFileRepoBtn').on('click', function () {
        $('#AddFileToRepoModal').modal();
    });
    $('#repoButton').on('click', function () {
        showRepo();
    });
    $("#fileBackgroundRepo").change(function () {
        $('#loadingSpinner').show();
        loadFileRepo();
        $('#loadingSpinner').hide();
    });
    $('#renameFileRepo').on('click', function () {
        bootbox.prompt({
            title: "Podaj Nową nazwę pliku",
            centerVertical: true,
            value: repoItemName
            ,
            callback: function (result) {
                if (result) {

                    $.ajax({
                        url: '/api/repository/' + repoItem + '/',
                        type: 'put',
                        data: {'visible_name': result}
                        ,
                        success: function (result) {
                            $('#loadingSpinner').hide();
                            location.reload();
                        }
                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });

                }
            }
        });
    });
    $('#removeFileRepo').on('click', function () {
        bootbox.confirm({
            message: "Czy napewno chesz usunąć plik ?",
            centerVertical: true
            ,
            callback: function (result) {
                if (result) {
                    $.ajax({
                        url: '/api/repository/' + repoItem + '/',
                        type: 'delete',
                        success: function (result) {
                            $('#loadingSpinner').hide();
                            location.reload();
                        }
                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });
                }
            }
        });
    });


    $('.voteButtons').on('click', function () {
        vote = $(this).attr('data-value');
        $('#loadingSpinner').show();
        $.post('/api/projects/' + selectedProject + '/vote/', {
            'rate': vote * 10
        }, function (result) {
            dataLoadProject();
            $('#loadingSpinner').hide();
            $('#voteModal').modal('hide');
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        })
    });
    setDefaultCookie();
    AddLastProject(0);
    ZmianaTrybuPracy();
    //dodanie przycisku dodającego nowe środowisko
    //event pokazujący sidebar
    $('#sidebarViewer').on('click', function () {
        $('#sidebar').toggleClass('active-sidebar sidebar2 ', 1000);
        $('#viewport').toggleClass('activeViewPort', 1000);
    });
    //przycisk wracający do listy środowisk
    $('#enviList').on('click', function () {
        trybPracy = 1;
        ZmianaTrybuPracy();
    });
    //po kliknięciu ostatnich projektów również wracamy do listy środowisk
    $('#lastProjectsList').on('click', function () {
        trybPracy = 1;
        ZmianaTrybuPracy();
    });
    //lista wszystkich projektów
    $('#allProjectsList').on('click', function () {
        trybPracy = 2;
        selectedEnvi = 'Wszystkie Projekty ';
        WybraneSrodowisko = 0;
        ZmianaTrybuPracy();
    });
    EventEnviClick();
    EventProjectClick
    LoadLastProjectList();
    //scroll
    $(window).scroll(function () {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
            pageLoad++;
            if (trybPracy === 1) {
                if (stopReadPage === 0)

                    $.post('/front/environments/', {
                        'keyword': '',
                        'page': pageLoad
                    }, function (result, state, status) {
                        if (status['status'] == 200) {
                            result = result.trim();
                            if (result == "") stopReadPage = 1;
                            else {
                                $('#allEnvi').append(result);
                            }
                        } else bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });

            }
            if (trybPracy == 2) {
                if (stopReadPage === 0) {
                    $.post('/front/projects/', {
                        'keyword': '',
                        'numEnvi': WybraneSrodowisko,
                        'page': pageLoad
                        ,
                        'category_id': $('#categoryProjectSearch').val()
                    }, function (result, state, status) {
                        if (status['status'] == 200) {
                            result = result.trim();
                            if (result == "") stopReadPage = 1;
                            else {
                                $('#allProject').append(result);
                            }
                        } else bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });
                    ;
                }

            }
        }

    });
    //wyszukiwanie środowiska
    $('#searchEnvi').on('keyup', function () {
        keyword = $(this).val();
        if ($(this).val() == "") {
            search = 0;
            pageLoad = 1;
            stopReadPage = 0;
            $('#allEnvi').html('');
            $.post('/front/environments/', {
                'keyword': '',
                'page': pageLoad
            }, function (result, state, status) {
                if (status['status'] == 200) {
                    result = result.trim();
                    if (result == "") stopReadPage = 1;
                    else {
                        $('#allEnvi').append(result);
                    }
                } else bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            }).fail(function () {
                $('#loadingSpinner').hide();
                bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            });
        } else {
            search = 1;
            pageLoad = 1;
            stopReadPage = 0;
            $('#allEnvi').html('');
            $.post('/front/environments/', {
                'keyword': keyword,
                'page': pageLoad
            }, function (result, state, status) {
                if (status['status'] == 200) {
                    result = result.trim();
                    if (result == "") stopReadPage = 1;
                    else {
                        $('#allEnvi').append(result);
                    }
                } else bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            }).fail(function () {
                $('#loadingSpinner').hide();
                bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            });
        }
    });
    //wyszukiwanie projektów w środowisku

    $('#categoryProjectSearch').on('change', function () {
        $('#loadingSpinner').show();
        search = 1;
        pageLoad = 1;
        stopReadPage = 0
        $('#allProject').html('');
        $.post('/front/projects/', {
            'keyword': keyword,
            'numEnvi': WybraneSrodowisko,
            'page': pageLoad,
            'category_id': $('#categoryProjectSearch').val()
        }, function (result, state, status) {
            if (status['status'] == 200) {
                result = result.trim();
                if (result == "") stopReadPage = 1;
                else {
                    $('#allProject').append(result);
                }
                $('#loadingSpinner').hide();
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
    });

    $('#searchProjectEnvi').on('keyup', function () {
        $('#loadingSpinner').show();
        keyword = $(this).val();
        if ($(this).val() == "") {
            search = 0;
            pageLoad = 1;
            stopReadPage = 0
            $('#allProject').html('');
            $.post('/front/projects/', {
                'keyword': '',
                'numEnvi': WybraneSrodowisko,
                'page': pageLoad
                ,
                'category_id': $('#categoryProjectSearch').val()
            }, function (result, state, status) {
                if (status['status'] == 200) {
                    result = result.trim();
                    if (result == "") stopReadPage = 1;
                    else {
                        $('#allProject').append(result);
                    }
                } else bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
                $('#loadingSpinner').hide();
            }).fail(function () {
                $('#loadingSpinner').hide();
                bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            });
            ;
        } else {
            search = 1;
            pageLoad = 1;
            stopReadPage = 0
            $('#allProject').html('');
            $.post('/front/projects/', {
                'keyword': keyword,
                'numEnvi': WybraneSrodowisko,
                'page': pageLoad,
                'category_id': $('#categoryProjectSearch').val()
            }, function (result, state, status) {
                if (status['status'] == 200) {
                    result = result.trim();
                    if (result == "") stopReadPage = 1;
                    else {
                        $('#allProject').append(result);
                    }
                } else bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
                $('#loadingSpinner').hide();
            }).fail(function () {
                $('#loadingSpinner').hide();
                bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            });
        }
    });
}

function LoadLastProjectList() {
    $('.lastprojectitems').remove();
    lastid = [];
    lastid.push($.cookie('save' + currentUser + 'Project1'));
    lastid.push($.cookie('save' + currentUser + 'Project2'));
    lastid.push($.cookie('save' + currentUser + 'Project3'));


    lastid.forEach(function (element, index, array) {
        if (element != 0) {

            $.get('/api/projects/' + element, function (result) {
                $('#lastProjectsList').after($('<li>').append($('<a>').addClass('l2 lastprojectitems').append($('<i>').addClass('fas fa-tasks'), result['project_name'])).on('click', function () {
                    selectedProject = element;
                    selectedProjectName = result['project_name'];
                    selectedEnvi = result['environment_name'];
                    WybraneSrodowisko = result['environment'];
                    if (result['cover_image'] != null)
                        backgroundurl = result['cover_image'];
                    else
                        backgroundurl = "";
                    trybPracy = 5;
                    ZmianaTrybuPracy();
                }));
            }).fail(function () {
                $('#loadingSpinner').hide();
                $.cookie('save' + currentUser + 'Project' + (index + 1), 0);
            });

        }
    });


}

function ZmianaTrybuPracy() {
    $('#loadingSpinner').show();
    $('#mainPage').hide();
    $('#listProjects').hide();
    $('#editEnvi').hide();
    $('#permEnvi').hide();
    $('#projectPage').hide();
    $('#permProject').hide();
    $('#editProject').hide();
    $('#editEnviContent').html('');
    $('#editPermContent').html('');
    $('#editProjectContent').html('');
    $('#editPermProjectContent').html('');
    $('#projectPageContent').html('');
    $('#allEnvi').html('');
    $('#lastSearch').html('');
    $('.projectListButtons').remove();
    if ($('#selectedEnviList').length) $('#selectedEnviList').remove();
    $('#addNew').remove();
    $('#editProjectInsideBtn').hide();
    pageLoad = 1;
    search = 0;
    stopReadPage = 0;
    keyword = "";

    if (trybPracy == 1) {
        backgroundurl = "";
        addNewEnviButton();
        $('#mainPage').fadeIn();
        lastProjectContent = "";
        for (var i = 1; i < 4; i++) {
            if ($.cookie('save' + currentUser + 'Project' + i) && $.cookie('save' + currentUser + 'Project' + i) != 0) {
                $.post('/front/projects/', {
                    'keyword': '',
                    'page': 0,
                    'numEnvi': 0,
                    'id_project': $.cookie('save' + currentUser + 'Project' + i)
                }, function (result, state, status) {
                    if (status['status'] == 200) {
                        lastProjectContent += result.trim();
                        $('#lastSearch').html(lastProjectContent);
                    } else bootbox.alert({
                        message: "Wystąpił błąd",
                        centerVertical: true,
                    });


                }).fail(function () {
                    $('#loadingSpinner').hide();
                    bootbox.alert({
                        message: "Wystąpił błąd",
                        centerVertical: true,
                    });
                });
            }
        }


        $.post('/front/environments/', {
            'keyword': '',
            'page': pageLoad
        }, function (result, state, status) {
            if (status['status'] == 200) {
                $('#allEnvi').html(result);
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
            $('#loadingSpinner').hide();

        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });


    }
    if (trybPracy == 2) {
        $("#categoryProjectSearch").val($("#categoryProjectSearch option:first").val());

        $('#headerListProjects').html(selectedEnvi);
        $('#listProjects').fadeIn();
        $.post('/front/projects/', {
            'keyword': '',
            'numEnvi': WybraneSrodowisko,
            'page': pageLoad
            ,
            'category_id': $('#categoryProjectSearch').val()
        }, function (result, state, status) {
            if (status['status'] == 200) {


                $('#allProject').html(result);
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
            $('#loadingSpinner').hide();

        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });

        addNewEnviButton();
        addCurrentEnviButton();
        addProjectButton();
    }
    if (trybPracy === 3) {
        $('#editEnvi').fadeIn();
        if (WybraneSrodowisko != 0)
            $('#headerEditEnvi').html('Edycja ' + selectedEnvi);
        else
            $('#headerEditEnvi').html('Dodaj Środowisko');
        $.post('/front/editEnvi', {
            'numEnvi': WybraneSrodowisko
        }, function (result, state, status) {
            if (status['status'] == 200) {
                result = result.trim();
                $('#editEnviContent').html(result);
                editEnviEvents();
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
            $('#loadingSpinner').hide();
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
        addNewEnviButton();
        if (WybraneSrodowisko != 0)
            addCurrentEnviButton();
    }
    if (trybPracy === 4) {
        $.post('/front/environmentsperms/', {
            'environment_id': WybraneSrodowisko
        }, function (result, state, status) {
            if (status['status'] == 200) {
                $('#permEnvi').fadeIn();
                $('#headerPermEnvi').html('Uprawnienia ' + selectedEnvi);
                result = result.trim();
                $('#editPermContent').html(result);
                addPermEnvi();
                addNewEnviButton();
                addCurrentEnviButton();
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
            $('#loadingSpinner').hide();

        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
    }
    if (trybPracy === 5) {
        $.post('/front/project/', {
            'project_id': selectedProject
        }, function (result, state, status) {
            if (status['status'] == 200) {
                $('#projectPage').fadeIn();
                $('#headerProjectContent').html('Projekt ' + selectedProjectName);
                result = result.trim();
                $('#projectPageContent').html(result);
                AddLastProject(selectedProject);
                addCurrentEnviButton();
                addNewEnviButton();
                addCurrentProjectButton()
                addProjectButton();
                projectEvents();
                dataLoadProject();

            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
            $('#loadingSpinner').hide();
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
    }
    if (trybPracy === 6) {

        $.post('/front/editProject', {
            'id': selectedProject
        }, function (result, state, status) {
            if (status['status'] == 200) {
                if (selectedProject == 0)
                    $('#headerEditProject').html('Dodaj Projekt');
                else
                    $('#headerEditProject').html('Edycja ' + selectedProjectName);
                $('#editProject').fadeIn();

                result = result.trim();
                $('#editProjectContent').html(result);
                addNewEnviButton();
                addCurrentEnviButton();
                if (selectedProject != 0)
                    addCurrentProjectButton()
                addProjectButton();
                editProjectEvent();
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
            $('#loadingSpinner').hide();
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
    }
    if (trybPracy === 7) {
        $.post('/front/projectperms/', {
            'project_id': selectedProject
        }, function (result, state, status) {
            if (status['status'] == 200) {
                $('#permProject').fadeIn();
                $('#headerPermProject').html('Uprawnienia ' + selectedProjectName);
                result = result.trim();
                $('#editPermProjectContent').html(result);
                deletePermProject();
                addNewEnviButton();
                addCurrentEnviButton();
                addCurrentProjectButton();
                addProjectButton();
                permProjectEvents();
                $('#loadingSpinner').hide();
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
    }
    setBackgroundImage();
}

function addProjectButton() {
    if (WybraneSrodowisko != 0) {
        $.post('/api/canAddProject', {

            'id': WybraneSrodowisko
        }, function (result, state, status) {
            if (status['status'] == 200) {

                if (result != null && result['can_add'] == true) {
                    $('#allProjectsList').after($('<li>').append($('<a>').addClass('l2 projectListButtons').attr('id', 'addNew').attr('role', 'button').append($('<i>').addClass('fas fa-plus'), ' Dodaj Projekt')).on('click', function () {
                        selectedProject = 0;
                        selectedProjectName = "Dodaj Projekt";
                        trybPracy = 6;
                        ZmianaTrybuPracy();
                    }));
                }
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });


    }
}

function addCurrentProjectButton() {
    $('#allProjectsList').after($('<li>').append($('<a>').addClass('l2 projectListButtons').attr('id', 'curren').attr('role', 'button').append($('<i>').addClass('fas fa-tasks'), selectedProjectName)).on('click', function () {
        trybPracy = 5;
        ZmianaTrybuPracy();
    }));
}

function addCurrentEnviButton() {
    $('#enviList').after($('<li>').append($('<a>').addClass('l2').attr('id', 'selectedEnviList').attr('role', 'button').append($('<i>').addClass('far fa-object-ungroup'), selectedEnvi)).on('click', function () {
        trybPracy = 2;
        ZmianaTrybuPracy();
    }));
}

function addNewEnviButton() {
    $.post('/api/canAddEnvi',
        function (result, state, status) {
            if (status['status'] == 200) {
                if (result != null && result['can_add'] == true) {
                    $('#enviList').after($('<li>').append($('<a>').addClass('l2').attr('id', 'addNew').attr('role', 'button').append($('<i>').addClass('fas fa-plus'), ' Dodaj Środowisko')).on('click', function () {
                        selectedEnvi = "";
                        WybraneSrodowisko = 0;
                        trybPracy = 3;
                        ZmianaTrybuPracy();
                    }));
                }
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        }).fail(function () {
        $('#loadingSpinner').hide();
        bootbox.alert({
            message: "Wystąpił błąd",
            centerVertical: true,
        });
    });
    ;

}

function disableLoading() {
    $('#loadingModal').modal('hide');
}

function setBackgroundImage() {
    if (backgroundurl == "")
        $('body').css('background-image', 'url(\'/static/pznsi/images/back1.jpg\')');
    else
        $('body').css('background-image', 'url(\'' + backgroundurl + '\')');
    $('body').css('z-index', '-1000');
}

function setDefaultCookie() {
    var date = new Date();
    date.setTime(date.getTime() + (364 * 24 * 60 * 60 * 1000));

    if (!$.cookie('save' + currentUser + 'Project1')) $.cookie('save' + currentUser + 'Project1', 0, {expires: date});
    if (!$.cookie('save' + currentUser + 'Project2')) $.cookie('save' + currentUser + 'Project2', 0, {expires: date});
    if (!$.cookie('save' + currentUser + 'Project3')) $.cookie('save' + currentUser + 'Project3', 0, {expires: date});

}

function AddLastProject(id) {
    var date = new Date();
    date.setTime(date.getTime() + (364 * 24 * 60 * 60 * 1000));
    if (id != 0 && $.cookie('save' + currentUser + 'Project3') != id && $.cookie('save' + currentUser + 'Project1') != id && $.cookie('save' + currentUser + 'Project2') != id) {
        $.cookie('save' + currentUser + 'Project3', $.cookie('save' + currentUser + 'Project2'), {expires: date});
        $.cookie('save' + currentUser + 'Project2', $.cookie('save' + currentUser + 'Project1'), {expires: date});
        $.cookie('save' + currentUser + 'Project1', id, {expires: date});
        LoadLastProjectList();

    }
}


//funkcje uprawnien srodowiska!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

function addPermEnvi() {
    $('select').selectpicker();
    $('#SearchPermUser').on('keyup', function () {
        var value = $(this).val().toLowerCase();
        $(".searchtr").filter(function () {

            $(this).parent().parent().toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    })
    $('.changePermCheckEnvi').on('change', function () {
        arr = [];
        arr.push($(this).attr('data-type-perm'));
        userId = $(this).attr('data-user-id');
        var operation = 'remove_permissions';
        if ($(this).is(':checked')) {
            operation = "add_permissions";
        }
        $('#loadingSpinner').show();
        $.ajax({
            type: "POST",
            url: '/api/environments/' + WybraneSrodowisko + '/' + operation + '/',
            data: JSON.stringify({
                permissions: arr,
                user_id: userId
            }),
            success: function () {
                $('#loadingSpinner').hide();
            },

            contentType: 'application/json',
            dataType: 'json'
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
    });


    $('.addPermEnvi').on('click', function () {
            arr = [];
            if ($('#permAddEnvi').is(':checked'))
                arr.push('edit_environment_instance');
            if ($('#permViewEnvi').is(':checked'))
                arr.push('view_environment_instance');

            var user_id = $('#selectNewPermEnvi').val();
            if (user_id !== null) {
                $('#loadingSpinner').show();
                $.ajax({
                    type: "POST",
                    url: '/api/environments/' + WybraneSrodowisko + '/add_permissions/',
                    data: JSON.stringify({
                        permissions: arr,
                        user_id: user_id
                    }),
                    success: function () {
                        $('#loadingSpinner').hide();
                        ZmianaTrybuPracy();
                    },

                    contentType: 'application/json',
                    dataType: 'json'
                }).fail(function () {
                    $('#loadingSpinner').hide();
                    bootbox.alert({
                        message: "Wystąpił błąd",
                        centerVertical: true,
                    });
                });
            }

            ZmianaTrybuPracy();
        }
    );
    $('.deletePermEnvi').on('click', function () {
        //alert($(this).attr('data-user-perm-id'));
        //alert(WybraneSrodowisko);

        // $(this).parent().parent().hide();
        this1 = this;
        bootbox.confirm({
            message: "Czy napewno chcesz usunąć uprawnienia ?",
            buttons: {
                confirm: {
                    label: 'Tak',
                    className: 'btn-success'
                },
                cancel: {
                    label: 'Nie',
                    className: 'btn-danger'
                }
            },
            callback: function (result) {
                if (result) {
                    userId1 = $(this1).attr('data-user-perm-id');
                    $.ajax({
                        type: "POST",
                        url: '/api/environments/' + WybraneSrodowisko + '/remove_permissions/',
                        data: JSON.stringify({
                            permissions: ['edit_environment_instance', 'view_environment_instance'],
                            user_id: userId1
                        }),
                        success: function () {
                            $('#loadingSpinner').hide();
                            $(this1).parent().parent().parent().addClass('outItem', 1000);
                            $(this1).parent().parent().parent().hide(1000);
                        },

                        contentType: 'application/json',
                        dataType: 'json'
                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });
                }
            }
        });
    })
}

//funkcje uprawnien projektu !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
function permProjectEvents() {
    $('select').selectpicker();
    $('.changePermCheck').on('change', function () {
        arr = [];
        arr.push($(this).attr('data-type-perm'));
        userId = $(this).attr('data-user-id');
        var operation = 'remove_permissions';
        if ($(this).is(':checked')) {
            operation = "add_permissions";
        }
        $('#loadingSpinner').show();
        $.ajax({
            type: "POST",
            url: '/api/projects/' + selectedProject + '/' + operation + '/',
            data: JSON.stringify({
                permissions: arr,
                user_id: userId
            }),
            success: function () {
                $('#loadingSpinner').hide();
            },

            contentType: 'application/json',
            dataType: 'json'
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });


    });

    $('.addPermProject').on('click', function () {
        arr = [];
        if ($('#newPermPod').is(':checked')) {
            arr.push('view_project_instance');
        }
        if ($('#newPermEdycja').is(':checked')) {
            arr.push('edit_project_instance');
        }
        if ($('#newPermOcena').is(':checked')) {
            arr.push('vote');
        }
        var user_id = $('#selectNewPermProject').val();
        if (user_id !== null) {
            $('#loadingSpinner').show();
            $.ajax({
                type: "POST",
                url: '/api/projects/' + selectedProject + '/add_permissions/',
                data: JSON.stringify({
                    permissions: arr,
                    user_id: user_id
                }),
                success: function () {
                    $('#loadingSpinner').hide();
                    ZmianaTrybuPracy();
                },

                contentType: 'application/json',
                dataType: 'json'
            }).fail(function () {
                $('#loadingSpinner').hide();
                bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            });
        } else
            bootbox.alert({
                message: "Nie Wybrano użytkownika",
                centerVertical: true,
            });


    });


    $('#SearchPermUser').on('keyup', function () {
        var value = $(this).val().toLowerCase();
        $(".searchtr").filter(function () {

            $(this).parent().parent().toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    })
}


function deletePermProject() {
    $('.deletePermProject').on('click', function () {
        var userId1 = $(this).attr('data-user-id');
        this1 = this;
        bootbox.confirm({
            message: "Czy napewno chcesz usunąć uprawnienia ?",
            buttons: {
                confirm: {
                    label: 'Tak',
                    className: 'btn-success'
                },
                cancel: {
                    label: 'Nie',
                    className: 'btn-danger'
                }
            },
            callback: function (result) {
                if (result) {
                    $('#loadingSpinner').show();
                    $.ajax({
                        type: "POST",
                        url: '/api/projects/' + selectedProject + '/remove_permissions/',
                        data: JSON.stringify({
                            permissions: ['vote', 'edit_project_instance', 'view_project_instance'],
                            user_id: userId1
                        }),
                        success: function () {
                            $('#loadingSpinner').hide();
                            $(this1).parent().parent().parent().addClass('outItem', 1000);
                            $(this1).parent().parent().parent().hide(1000);
                        },

                        contentType: 'application/json',
                        dataType: 'json'
                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });


                }
            }
        });

    })
}


//FUNKCJE PROJEKTU !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

function EventProjectClick() {

    selectedProject = 0;
    selectedProjectName = ""
    $(".ProjectListElement").on('click', function (event) {
        backgroundurl = "";
        selectedProject = $(this).attr('data-project-id');
        selectedProjectName = $(this).attr('data-project-name');
        WybraneSrodowisko = $(this).attr('data-project-envi-id');
        selectedEnvi = $(this).attr('data-project-envi-name');
        backgroundurl = $(this).attr('data-background');
        event.stopPropagation();
        event.stopImmediatePropagation();
        trybPracy = 5;
        ZmianaTrybuPracy();
        LoadLastProjectList();
    });
    $(".permProjectButton").on('click', function (event) {
        selectedProject = $(this).attr('data-project-id');
        selectedProjectName = $(this).attr('data-project-name');
        WybraneSrodowisko = $(this).attr('data-project-envi-id');
        selectedEnvi = $(this).attr('data-project-envi-name');
        backgroundurl = $(this).attr('data-background');
        event.stopPropagation();
        event.stopImmediatePropagation();
        trybPracy = 7;
        ZmianaTrybuPracy();
    });
    $(".removeProjectButton").on('click', function (event) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        e = this;
        projectNum = $(this).attr('data-project-id');
        bootbox.confirm("Czy napewno chcesz usunąć projekt ?", function (result) {
            if (result) {
                $('#loadingSpinner').show();
                $.ajax({
                    url: '/api/projects/' + projectNum + '/',
                    type: 'delete',
                    success: function (result) {
                        $('#loadingSpinner').hide();
                        $(e).parent().parent().parent().fadeOut(100);
                        LoadLastProjectList();
                    }
                }).fail(function () {
                    $('#loadingSpinner').hide();
                    bootbox.alert({
                        message: "Wystąpił błąd",
                        centerVertical: true,
                    });
                });
            }
        });

    });
    $(".editProjectButton").on('click', function (event) {
        selectedProject = $(this).attr('data-project-id');
        selectedProjectName = $(this).attr('data-project-name');
        WybraneSrodowisko = $(this).attr('data-project-envi-id');
        selectedEnvi = $(this).attr('data-project-envi-name');
        backgroundurl = $(this).attr('data-background');

        event.stopPropagation();
        event.stopImmediatePropagation();
        trybPracy = 6;
        ZmianaTrybuPracy();
    })


}

function checkSizeFile(file) {
    return file.size < 20000000;
}

//zmiana pliku na base64
function getBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

//podzial wielkosci komentarzy i zalaczników w projekcie
/**
 * @return {number}
 */
function PodzialWielkosciKomentarzyZalacznikow(str) {
    if (str.length < 80) return 4;
    if (str.length > 200) return 12;
    else return 6;
}

//rozmieszczenie komentarzy i zalacznikow
function showContent(data, len) {
    var d = new Date(data['date']);
    dformat = [d.getMonth() + 1,
            d.getDate(),
            d.getFullYear()].join('/') + ' ' +
        [d.getHours(),
            d.getMinutes(),
            d.getSeconds()].join(':');

    var element = "";
    var editElement = $('<span>').addClass('dropdown-item EditCommentItem').attr('data-item-id', data['id']).attr('data-comment-value', data['data']).attr('data-type-item', data['type']).html('Edytuj')
    if (data['type'] !== "comment") editElement = '';
    var menuElement = $('<div>').addClass('dropdown dropdownStyle').append(
        $('<button>').attr('id', 'dropdownInfo').addClass('btn').attr('type', 'button').attr('data-toggle', 'dropdown').attr('aria-haspopup', 'true').attr('aria-expanded', 'false').append(
            $('<i>').addClass('fa reversColor fa-ellipsis-v').attr('aria-hidden', 'true')
        ),
        $('<div>').addClass('dropdown-menu dropdown-menu-right').attr('aria-labelledby', 'dropdownInfo').append(
            $('<span>').addClass('dropdown-item removeItemCommentAttachment').attr('data-item-id', data['id']).attr('data-type-item', data['type']).html('Usuń'),
            editElement
        )
    );
    if (data['can_edit'] == false) menuElement = "";
    if (data['UserIco'] === null) {
        data['UserIco'] = '/static/pznsi/images/user.ico';
    }
    if (data['type'] === "comment") {
        element = $('<div>').addClass('col-lg-' + len + ' p-3').append(
            $('<div>').addClass('bgw p-3 mh-100').append(
                menuElement,
                $('<h4>').append(
                    $('<img>').addClass('comIco').attr("src", data['UserIco'])
                    , ' ',
                    data['User'], ' ',
                    $('<span>').addClass('dateFormat').html(dformat)
                ),
                $('<p>').html(data['data'])
            )
        );
    }
    if (data['type'] === "attachment") {
        var showElement = $('<span>');
        arr = data['data'].split('.');
        FTtxt = ['txt', 'md', 'rtf'];
        FTpdf = ['pdf'];
        FTaudio = ['mp3', 'wav', 'flac'];
        FTarchive = ['7z', 'zip', 'rar', 'gz', 'tar'];
        FTvideo = ['avi', 'mpg', 'webm', 'mp4', 'ogg', 'mpeg', 'fly'];
        FTword = ['odt', 'doc', 'docx'];
        FTexcel = ['xls', 'xlsx', 'calc'];
        FTcode = ['py', 'java', 'c', 'cpp', 'js', 'html', 'htm', 'xhtml', 'xml', 'json', 'css', 'php'];

        if (arr[arr.length - 1] == 'jpg' || arr[arr.length - 1] == 'jpeg' || arr[arr.length - 1] == 'gif' || arr[arr.length - 1] == 'bmp' || arr[arr.length - 1] == 'png ') {
            showElement.append($('<img>').attr('src', data['data']).css('height', '3em').css('display', 'block').css('margin', '0px auto').addClass('text-center justify-content-center')).addClass('w-100 ');
        } else if (FTtxt.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-alt fileComment');
        else if (FTpdf.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-pdf fileComment');
        else if (FTaudio.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-audio fileComment');
        else if (FTarchive.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-archive fileComment');
        else if (FTvideo.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-video fileComment');
        else if (FTword.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-word fileComment');
        else if (FTcode.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-code fileComment');
        else if (FTexcel.includes(arr[arr.length - 1])) showElement.addClass('fa fa-3x fa-file-excel fileComment');
        else {
            showElement.addClass('fa fa-3x fa-file fileComment');
        }

        element = $('<div>').addClass('col-lg-' + len + ' p-3').append(
            $('<div>').addClass('bgw p-3 mh-100').append(
                menuElement,
                $('<h4>').append(
                    $('<img>').addClass('comIco').attr("src", data['UserIco']), ' ', data['User'], ' ', $('<span>').addClass('dateFormat').html(dformat)
                ),
                $('<a>').attr('href', data['data']).attr('target', '_blank').addClass('fileComment justify-content-center text-center').css('text-decoration', 'none').css('color', 'black').append(showElement, $('<h4>').html(data['attachment_name']))
            )
        );
    }
    $('#commentAttachmentProject').append(element);
}

function loadComments() {

    $('#commentAttachmentProject').html('');
    //tu będzie post na wyciągnięcie danych
    for (var i = 0; i < dataCommentAttachment.length; i++) {
        sum = 0;
        p1 = 0
        if (dataCommentAttachment[i]['type'] === "comment")
            p1 = PodzialWielkosciKomentarzyZalacznikow(dataCommentAttachment[i]['data']);
        else
            p1 = 4;
        p2 = 0;
        p3 = 0;
        if (i + 1 < dataCommentAttachment.length) {
            if (dataCommentAttachment[i + 1]['type'] === "comment")
                p2 = PodzialWielkosciKomentarzyZalacznikow(dataCommentAttachment[i + 1]['data']);
            else p2 = 4;
        }

        if (i + 2 < dataCommentAttachment.length) {
            if (dataCommentAttachment[i + 2]['type'] === "comment")
                p3 = PodzialWielkosciKomentarzyZalacznikow(dataCommentAttachment[i + 2]['data']);
            else p3 = 4;
        }

        if (p1 === 4) {
            if (p2 === 0) showContent(dataCommentAttachment[i], p1);
            else if (p2 === 4) {
                if (p3 === 0) {
                    showContent(dataCommentAttachment[i], p1);
                    showContent(dataCommentAttachment[i + 1], p2);
                    i++;
                }
                if (p3 === 4) {
                    showContent(dataCommentAttachment[i], p1);
                    showContent(dataCommentAttachment[i + 1], p2);
                    showContent(dataCommentAttachment[i + 2], p3);
                    i += 2;
                }
                if (p3 === 6) {
                    showContent(dataCommentAttachment[i], p1);
                    showContent(dataCommentAttachment[i + 1], p2);
                    showContent(dataCommentAttachment[i + 2], p3 - 2);
                    i += 2;
                }
                if (p3 === 12) {
                    showContent(dataCommentAttachment[i], p1 + 2);
                    showContent(dataCommentAttachment[i + 1], p2 + 2);
                    i++;
                }
            } else if (p2 === 6) {
                showContent(dataCommentAttachment[i], p1 + 2);
                showContent(dataCommentAttachment[i + 1], p2);
                i++;
            } else if (p2 === 12) {
                showContent(dataCommentAttachment[i], p1);
                showContent(dataCommentAttachment[i + 1], p2 - 4);
                i++;
            }
        } else if (p1 === 6) {
            if (p2 === 6) {
                showContent(dataCommentAttachment[i], p1);
                showContent(dataCommentAttachment[i + 1], p2);
                i++;
            } else if (p2 === 4) {
                showContent(dataCommentAttachment[i], p1);
                showContent(dataCommentAttachment[i + 1], p2 + 2);
                i++;

            } else if (p2 === 12) {
                showContent(dataCommentAttachment[i], p1);
                showContent(dataCommentAttachment[i + 1], p2 - 6);
                i++;

            } else if (p2 === 0) showContent(dataCommentAttachment[i], p1);
        } else if (p1 === 12) {
            showContent(dataCommentAttachment[i], p1);
        }


    }
    eventsCommentsAttachment();
}

function eventsCommentsAttachment() {
    $('.removeItemCommentAttachment').on('click', function () {
        var e = this;
        bootbox.confirm("Czy napewno chcesz usunąć ?", function (result) {
            if (result) {
                var action = '';
                var type = $(e).attr('data-type-item');
                var itemid = $(e).attr('data-item-id');
                if (type == "attachment") {
                    $('#loadingSpinner').show();
                    $.post('/api/projects/' + selectedProject + '/delete_attachment/', {
                        'attachment_id': itemid
                    }, function () {
                        $(e).parent().parent().parent().fadeOut();
                        dataLoadProject();
                        $('#loadingSpinner').hide();

                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });
                }
                if (type == "comment") {
                    $('#loadingSpinner').show();
                    $.post('/api/projects/' + selectedProject + '/delete_comment/', {
                        'comment_id': itemid
                    }, function () {
                        $(e).parent().parent().parent().fadeOut();
                        dataLoadProject();
                        $('#loadingSpinner').hide();

                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });
                }
            }
        });
    });
    $('.EditCommentItem').on('click', function () {
        var e = this;
        bootbox.prompt({
            title: "Edytuj Komentarz",
            inputType: 'textarea',
            value: $(e).attr('data-comment-value'),
            centerVertical: true,
            callback: function (result) {
                if (result) {
                    var itemid = $(e).attr('data-item-id');
                    $('#loadingSpinner').show();
                    $.post('/api/projects/' + selectedProject + '/edit_comment/', {
                        'comment_id': itemid,
                        'comment': result
                    }, function () {
                        dataLoadProject();
                        $('#loadingSpinner').hide();

                    }).fail(function () {
                        $('#loadingSpinner').hide();
                        bootbox.alert({
                            message: "Wystąpił błąd",
                            centerVertical: true,
                        });
                    });
                }
            }
        });
    })
}

//dodanie do projektu zalcznika
function addAttachmentToProject() {
    bootbox.prompt({
        title: "Podaj tutuł pliku ", centerVertical: true, callback: function (out1) {
            if (out1 != null) {
                $('#loadingSpinner').show();
                var fd = new FormData();
                var files = FileToUploadAttachment;
                fd.append('file', files);
                fd.append('title', out1);
                $.ajax({
                    url: '/api/projects/' + selectedProject + '/add_attachment/',
                    type: 'post',
                    data: fd,
                    contentType: false,
                    processData: false,
                    success: function (response) {
                        $('#loadingSpinner').hide();
                        dataLoadProject();
                        bootbox.alert({
                            message: "Dodano plik",
                            centerVertical: true,
                        });
                    },
                }).fail(function () {
                    $('#loadingSpinner').hide();
                    bootbox.alert({
                        message: "Wystąpił błąd",
                        centerVertical: true,
                    });
                });
            }
        }
    });

}

//zaladowanie danych do projektu
function dataLoadProject() {
    $.get('/api/projects/' + selectedProject + '/', function (result) {
        myVote = "BRAK";
        votes = result['votes'];
        for (var i = 0; i < votes.length; i++) if (currentUser == votes[i]['user']['id']) myVote = votes[i]['vote_content'] / 10;
        $('.voteButtons').removeClass('active');
        if (myVote != "BRAK")
            $('.voteButtons[data-value|=' + myVote + ']').addClass('active');


        $('#myVote').html(myVote);
        if (result['vote_average'] == null)
            $('#avgVal').html('BRAK');
        else
            $('#avgVal').html(result['vote_average'] / 10);
        var datal = [];
        for (var i = 0; i < result['comments'].length; i++) {
            datal.push({
                type: "comment",
                User: result['comments'][i]['user']['username'],
                UserIco: result['comments'][i]['user']['avatar'],
                data: result['comments'][i]['comment_content'],
                date: result['comments'][i]['date'],
                id: result['comments'][i]['id'],
                can_edit: result['comments'][i]['can_edit'],
                attachment_name: ''
            });
        }
        for (var i = 0; i < result['attachments'].length; i++) {
            datal.push({
                type: "attachment",
                User: result['attachments'][i]['user']['username'],
                UserIco: result['attachments'][i]['user']['avatar'],
                data: result['attachments'][i]['content'],
                date: result['attachments'][i]['date'],
                id: result['attachments'][i]['id'],
                can_edit: result['attachments'][i]['can_edit'],
                attachment_name: result['attachments'][i]['attachment_name']
            });
        }
        dataCommentAttachment = datal;
        dataCommentAttachment.sort(function (a, b) {
            var da = new Date(a['date']);
            var db = new Date(b['date']);
            if (da.getTime() > db.getTime())
                return -1
            if (da.getTime() < db.getTime())
                return 1
            // a równe b
            return 0
        });
        loadComments();

    }).fail(function () {

    });

    //okno glosowania
    $('#voteButton').on('click', function () {
        $('#voteModal').modal();
    });


}

// definicja eventów po otwarciu projektu
function projectEvents() {
    //po kliknięciu przycisku obok nazwy projektu na projekcie przechodzimy do edycji
    $('#editProjectInsideBtn').on('click', function () {
        trybPracy = 6;
        ZmianaTrybuPracy();
    });
    //eventy obsługujące drag n drop na załącznikach
    $("html").on("dragover", function (e) {
        e.preventDefault();
        e.stopPropagation();
    });

    $("html").on("drop", function (e) {
        e.preventDefault();
        e.stopPropagation();
    });
    $('#addFileContent > span').on('dragenter', function (e) {
        e.stopPropagation();
        e.preventDefault();
        $('#addFileContent').addClass('border-blue');
        $(this).addClass('fa-file-upload');
        $(this).removeClass('fa-file');

    });
    $('#addFileContent > span').on('drop', function (e) {
        $('#loadingSpinner').show();
        e.stopPropagation();
        e.preventDefault();
        $('#fileAttachmentProject')[0].files = e.originalEvent.dataTransfer.files;
        FileToUploadAttachment = $('#fileAttachmentProject')[0].files[0];
        addAttachmentToProject();
        $('#addFileContent').removeClass('border-blue');
        $(this).addClass('fa-file-upload');
        $(this).removeClass('fa-file');
    });

    $('#addFileContent > span').click(function () {
        $('#loadingSpinner').show();
        $("#fileAttachmentProject").click();
    });
    $("#fileAttachmentProject").change(function () {
        $('#loadingSpinner').show();
        FileToUploadAttachment = $('#fileAttachmentProject')[0].files[0];
        addAttachmentToProject();
        $('#loadingSpinner').hide();
    });
    //navbar okienka statystyk
    $('.statNavItem').on('click', function () {
        $('.statNavItem').removeClass('active');
        $(this).addClass('active');
        if ($(this).attr('data-type') === "chart") {
            $('#ChartProject').show();
            $('#ListVoters').hide();
        }
        if ($(this).attr('data-type') === "list") {
            $('#ChartProject').hide();
            $('#ListVoters').show();
        }
    });

    //obsluga przycisku nowego komentarza
    $('#newCommentButton').on('click', function () {
        $('#loadingSpinner').show();
        var dane = $('#newCommentContent').val();
        $.post('/api/projects/' + selectedProject + '/add_comment/', {
            'comment': dane
        }, function (result) {
            dataLoadProject();
            $('#loadingSpinner').hide();
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });

        $('#newCommentContent').val('');

    });
    //zaladowanie statystyk po kliknieciu
    $('#statsButton').on('click', function () {
        $('#ListVoters').hide();
        $('#ChartProject').show();
        $('.statNavItem').removeClass('active');
        $('.statNavItem:first').addClass('active');
        dataChart = [];
        $('#ListVotersTbody').html('');
        for (var i = 0; i < 10; i++) dataChart[i] = 0;
        for (var i = 0; i < votes.length; i++) {
            dataChart[votes[i]['vote_content'] / 10 - 1]++;
            if (votes[i]['user']['avatar'] == null || votes[i]['user']['avatar'] === '') votes[i]['user']['avatar'] = '/static/pznsi/images/user.ico';
            $('#ListVotersTbody').append($('<tr>').append($('<td>').append($('<img>').addClass('comIco').attr('src', votes[i]['user']['avatar']), votes[i]['user']['username']), $('<td>').html(votes[i]['vote_content'] / 10)))

        }

        var ctx = document.getElementById('ChartProject').getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'pie',// 'horizontalBar',
            data: {
                labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                datasets: [{
                    label: 'Ilość Ocen',
                    data: dataChart,
                    backgroundColor: [

                        '#ff0000',
                        '#ffa500',
                        '#ffff00',
                        '#008000',
                        '#0000ff',
                        '#4b0082',
                        '#ee82ee',
                        '#707ece',
                        '#97548e',
                        '#254855'

                    ],
                    borderColor: [

                        '#ff0000',
                        '#ffa500',
                        '#ffff00',
                        '#008000',
                        '#0000ff',
                        '#4b0082',
                        '#ee82ee',
                        '#707ece',
                        '#97548e',
                        '#254855'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });


        $('#statsModal').modal();
    });
}

//FUNKCJE REPOOOOOOOOOOOOOOOOOOoo
function showRepo() {
    $('#repoContent').toggle();
}

//zapisanie pliku do repozytorium
function loadFileRepo() {

    fileRepo = $('#fileBackgroundRepo')[0].files[0];
    if (fileRepo != null) {
        if (checkSizeFile(fileRepo)) {
            $('#loadingSpinner').show();
            bootbox.prompt({
                title: "Podaj Nazwę pliku ", centerVertical: true, callback: function (resultPrompt) {
                    if (resultPrompt) {
                        var fd = new FormData();
                        fd.append('file', fileRepo);
                        fd.append('visible_name', resultPrompt);
                        $.ajax({
                            url: '/api/repository/',
                            type: 'post',
                            data: fd,
                            contentType: false,
                            processData: false,
                            success: function (response) {
                                $('#AddFileToRepoModal').modal('hide');
                                $('#loadingSpinner').hide();

                                bootbox.alert({
                                    message: "Dodano plik",
                                    centerVertical: true,
                                });
                                location.reload();
                            },
                        }).fail(function () {
                            $('#loadingSpinner').hide();
                            bootbox.alert({
                                message: "Wystąpił błąd",
                                centerVertical: true,
                            });
                        });
                    }
                }
            });

        }

    } else {
        bootbox.alert({
            message: "Plik jest za duży.Max 30 MB",
            centerVertical: true,
        });
        $('#loadingSpinner').hide();
    }

}


//edycja projektu !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
function SendFormEditProject() {
    var dateStart = new Date($('#startVoteDate').val());
    var dateend = new Date($('#endVoteDate').val());
    if (dateStart.getTime() > dateend.getTime()) {

        bootbox.alert({
            message: "Data początkowa nie może być większa od końcowej !",
            centerVertical: true,
        });
    } else {

        $('#loadingSpinner').show();

        $.post('/api/editprojectSave', {
            'cover_image': selectedFile,
            'owner': $('#owner_id').val(),
            'environment_id': WybraneSrodowisko,
            'project_name': $('#editProject_nameProject').val(),
            'project_description': $('#editProject_nameDesciption').val(),
            'project_category': $('#category_id').val(),
            'project_id': $('#project_id').val(),
            'startVoteDate': $('#startVoteDate').val(),
            'endVoteDate': $('#endVoteDate').val()
        }, function (result, state, status) {
            if (status['status'] == 200) {
                if (result != null) {
                    if (result['project_name'] != "") {
                        selectedProject = result['project_id'];
                        selectedProjectName = $('#editProject_nameProject').val();
                        backgroundurl = result['cover_image'];
                        LoadLastProjectList();
                        trybPracy = 5;
                        ZmianaTrybuPracy();
                    } else bootbox.alert({
                        message: "Wystąpił błąd",
                        centerVertical: true,
                    });
                } else bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        }).fail(function () {
            $('#loadingSpinner').hide();
            bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        });
        $('#loadingSpinner').hide();
    }
}

function setImageProjectBackground() {
    $('#loadingSpinner').show();
    file = $('#fileBackground')[0].files[0];
    if (file != null) {
        if (checkSizeFile(file)) {
            if (checkFileTypes(file)) {
                getBase64(file).then(
                    data => {
                        selectedFile = data;
                        $('#backgroundEx').css('background-image', "url('" + data + "')")
                        $('#loadingSpinner').hide();
                    }
                );
            } else {
                bootbox.alert({
                    message: "Dozwolone są tylko obrazy ! ",
                    centerVertical: true,
                });
                $('#loadingSpinner').hide();
            }
        } else {

            bootbox.alert({
                message: "Plik jest za duży.Max 30 MB",
                centerVertical: true,
            });
            $('#loadingSpinner').hide();
        }

    } else $('#loadingSpinner').hide();
}

function checkFileTypes(file) {
    acceptmimetypes = ['image/apng', 'image/bmp', 'image/gif', 'image/jpeg', 'image/png'];
    for (var item of acceptmimetypes) if (item == file.type) return true;
    return false;
}

function editProjectEvent() {
    flatpickr("startVoteDate");
    $('#startVoteDate').flatpickr({
        enableTime: true,
        dateFormat: "Y-m-d H:i",
    });
    $('#endVoteDate').flatpickr({
        enableTime: true,
        dateFormat: "Y-m-d H:i"

    });
    $("html").on("dragover", function (e) {
        e.preventDefault();
        e.stopPropagation();
        $("#editProject_dragName").text("Przeciągnij tu ");
    });

    $("html").on("drop", function (e) {
        e.preventDefault();
        e.stopPropagation();
    });
    $('.upload-area').on('dragenter', function (e) {
        e.stopPropagation();
        e.preventDefault();
        $("#editProject_dragName").text("Upuść tu ");
    });
    $('.upload-area').on('dragover', function (e) {
        e.stopPropagation();
        e.preventDefault();
        $("#editProject_dragName").text("Upuść tu ");
    });
    $('.upload-area').on('drop', function (e) {

        e.stopPropagation();
        e.preventDefault();
        $("#editProject_dragName").text("ładowanie pliku");
        $('#fileBackground')[0].files = e.originalEvent.dataTransfer.files;
        setImageProjectBackground();
        $("#editProject_dragName").text("Kliknij lub przeciągnij aby dodać tło");
    });

    $("#uploadfile").click(function () {
        $("#fileBackground").click();
    });

    $("#fileBackground").change(function () {

        setImageProjectBackground();
    });
}

function SendForm(id, nameEnvi) {
    $('#loadingSpinner').show();
    $.post('/api/editEnviSave', {
        'cover_image': selectedFile,
        'owner': $('#owner_id').val(),
        'environment_name': $('#editEnvi_nameEnvi').val(),
        'numEnvi': id
    }, function (result, state, status) {
        if (status['status'] == 200) {
            if (result != null) {
                if (result['result'] == "1") {
                    backgroundurl = result['cover_image'];
                    trybPracy = 2;
                    ZmianaTrybuPracy();
                } else bootbox.alert({
                    message: "Wystąpił błąd",
                    centerVertical: true,
                });
            } else bootbox.alert({
                message: "Wystąpił błąd",
                centerVertical: true,
            });
        } else bootbox.alert({
            message: "Wystąpił błąd",
            centerVertical: true,
        });

    }).fail(function () {
        $('#loadingSpinner').hide();
        bootbox.alert({
            message: "Wystąpił błąd",
            centerVertical: true,
        });
    });
}

function editEnviEvents() {
    selectedFile = "";
    $("html").on("dragover", function (e) {
        e.preventDefault();
        e.stopPropagation();
        $("#editEnvi_dragName").text("Przeciągnij tu ");
    });

    $("html").on("drop", function (e) {
        e.preventDefault();
        e.stopPropagation();
    });
    $('.upload-area').on('dragenter', function (e) {
        e.stopPropagation();
        e.preventDefault();
        $("#editEnvi_dragName").text("Upuść tu ");
    });
    $('.upload-area').on('dragover', function (e) {
        e.stopPropagation();
        e.preventDefault();
        $("#editEnvi_dragName").text("Upuść tu ");
    });
    $('.upload-area').on('drop', function (e) {
        $('#loadingSpinner').show();
        e.stopPropagation();
        e.preventDefault();
        $("#editEnvi_dragName").text("ładowanie pliku");
        $('#fileBackground')[0].files = e.originalEvent.dataTransfer.files;
        setImageProjectBackground();
        $("#editEnvi_dragName").text("Kliknij lub przeciągnij aby dodać tło");
        $('#loadingSpinner').hide();
    });

    $("#uploadfile").click(function () {
        $("#fileBackground").click();
    });

    $("#fileBackground").change(function () {
        $('#loadingSpinner').show();
        setImageProjectBackground();
        $('#loadingSpinner').hide();
    });
}