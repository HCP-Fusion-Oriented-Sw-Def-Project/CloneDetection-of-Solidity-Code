'use strict';
var parser = require("solidity-parser-antlr")
var fs = require('fs');
var path = require('path');

var inputAddress = fs.readFileSync('/home/yfliu/paper_code/gasDetect/inputAddress').toString();
inputAddress = inputAddress.slice(0,inputAddress.length-1);
var outputAddress = '/home/yfliu/paper_data/gasPattern/gasDetectResult2.txt'
var filePath = path.resolve(inputAddress);
var countIndex = 0;
var countCompileFail = 0;
var flag = false;

fs.readdir(filePath,function(err,files){
	if(err){
		console.warn(err)
	}else{
		files.forEach(function(fileName){
			console.log("正在处理第 " + ++countIndex + " 个文件 : " + fileName);
			
			// 读取智能合约
			var filedir = path.join(filePath,fileName);

			// 解析智能合约
			var address = fileName.replace(/\.sol/g,"");
			var data = fs.readFileSync(filedir);
			var code = data.toString();
			var processedCode = code.replace(/&#39;/g,"\'");

			try{
				var result = parser.parse(processedCode,{loc : true});
			}catch(err){
    			console.error('Failed to parse, ' + address + '\n', err);
    			// fs.appendFileSync('/data/kongqp/gas_optimization/log/compileFail.txt', ++countCompileFail + ' : ' + address + '\r\n');
    			return;
			}



			if(result.children.length != 0){
				for(var i = 0; i < result.children.length; i++){
					if(result.children[i].type == 'ContractDefinition'){
						// 重复赋值
						fs.appendFileSync(outputAddress, countIndex + ' : ' + address + ' : ' + result.children[i].name + '\r\n');
						flag = false;
						detectPattern(result.children[i]);
						if (flag == true)
							fs.appendFileSync(outputAddress,"success" + '\r\n');
					}
				}
			}

		});
	}
});


function detectPattern(_AST){
	// 找出已赋值的state变量
	global.assignedStateVariableNames= [];

	for(var i = 0; i < _AST.subNodes.length; i++){
		if(_AST.subNodes[i].type == 'StateVariableDeclaration'){
			if(_AST.subNodes[i].variables[0].expression != null){
				assignedStateVariableNames.push(_AST.subNodes[i].variables[0].name);
				//fs.appendFileSync(outputAddress, _AST.subNodes[i].variables[0].name + " : " + _AST.subNodes[i].variables[0].expression.loc.start.line + '_' + _AST.subNodes[i].variables[0].expression.loc.start.column + ", " + _AST.subNodes[i].loc.end.line + '_' +_AST.subNodes[i].loc.end.column + '\r\n');
			}

		}
	}


	// 检查构造函数是否对这些变量重新赋值
	for(var i = 0; i < _AST.subNodes.length; i++){
		if(_AST.subNodes[i].type == 'FunctionDefinition'){
			if(_AST.subNodes[i].isConstructor){
				preOrderTraversel(_AST.subNodes[i].body);
			}

		}
	}

}


function preOrderTraversel(_AST){
	if(typeof _AST == 'string' || typeof _AST == 'number' || _AST == null){
		return;
	}
	if(_AST instanceof Array){
		// console.log();
	}else{
		if(_AST.hasOwnProperty('type')){
			if(_AST.type == 'BinaryOperation'){
				if(_AST.operator == '='){
					if(_AST.left.type == 'Identifier'){
						if(assignedStateVariableNames.indexOf(_AST.left.name) != -1){
							fs.appendFileSync(outputAddress, _AST.left.name + ':' + _AST.left.loc.start.line + ',' + _AST.left.loc.end.line + '\r\n');
							//fs.appendFileSync(outputAddress,"success" + '\r\n');
							flag = true;
						}
					}
				}
			}
		}
	}
	for(var key in _AST){
		preOrderTraversel(_AST[key]);	
	}
}