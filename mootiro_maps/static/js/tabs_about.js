// JavaScript Document

$(function(){
	$('#content-tabs').hide();
	var info;	
	var hash = window.location.hash;
	if (hash !='')
	{
		info = $(hash).html();
		$('.tabs li a[href="' + hash + '"]').parent().addClass('active');		
	} else {
		info = $('#content-tabs div:first-child').html();			
		$('.tabs li:first-child').addClass('active');		
	}
	$('#info').append('<div>' + info + '</div>').find('div').slideDown();
	$('.tabs li a').click(function(){
		$('.tabs li').removeClass('active');
		$(this).parent().addClass('active');
		var ancora = $(this).attr('href');
		var nome = ancora.substr(1, ancora.length);
		info = $('#content-tabs div[id="' + nome + '"]').html();
		$('#info').empty();
		$('#info').append('<div>' + info + '</div>').find('div').slideDown();
	return false();
	})
})