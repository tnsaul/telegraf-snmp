package main

import (
	"log"
	"os"
	"fmt"
	"encoding/json"
	"io/ioutil"
	"path/filepath"
	"sync"	
	//"bufio"
	//"strings"

	//"github.com/alecthomas/repr"
	"github.com/sleepinggenius2/gosmi/parser"

	//"github.com/influxdata/telegraf/internal/snmp"
	//"github.com/influxdata/telegraf/plugins/inputs"

	//"github.com/gosnmp/gosnmp"
)


// must init, append path for each directory, load module for every file
// or gosmi will fail without saying why
var m sync.Mutex
var once sync.Once
var cache = make(map[string]bool)

//will give all found folders to gosmi and load in all modules found in the folders
func LoadMibsFromPath(paths []string) error {
	var firstTime = true
		
	folders, err := walkPaths(paths)
	if err != nil {
		return err
	}

	writeFile("[")

	for _, path := range folders {
		//loader.appendPath(path)
		log.Printf("Trying load PATH MIBS - %v", path)
		modules, err := ioutil.ReadDir(path)
		if err != nil {
			log.Printf("Can't read directory %v", modules)
		}

		for _, info := range modules {
			if info.Mode()&os.ModeSymlink != 0 {
				symlink := filepath.Join(path, info.Name())
				target, err := filepath.EvalSymlinks(symlink)
				if err != nil {
					log.Printf("Couldn't evaluate symbolic links for %v: %v", symlink, err)
					continue
				}
				//replace symlink's info with the target's info
				info, err = os.Lstat(target)
				if err != nil {
					log.Printf("Couldn't stat target %v: %v", target, err)
					continue
				}
			}
			if info.Mode().IsRegular() {
				log.Printf("Trying load module %v", info.Name())
				data, err := parseFile(path,info.Name())
				if err != nil {
					log.Printf("Couldn't load module %v: %v", info.Name(), err)
					continue
				}
				if !firstTime{
					// This looks odd, but it is actually writing a "," between json outputs
					writeFile(",")
				}
				firstTime = false
				writeFile("{\"" + info.Name() + "\": " + data + "}")
			}
		}
	}

	writeFile("]")
	return nil
}

//should walk the paths given and find all folders
func walkPaths(paths []string) ([]string, error) {

	folders := []string{}

	for _, mibPath := range paths {
		// Check if we loaded that path already and skip it if so
		m.Lock()
		cached := cache[mibPath]
		cache[mibPath] = true
		m.Unlock()
		if cached {
			continue
		}

		err := filepath.Walk(mibPath, func(path string, info os.FileInfo, err error) error {
			if info == nil {
				log.Printf("WARN: No mibs found")
				if os.IsNotExist(err) {
					log.Printf("WARN: MIB path doesn't exist: %q", mibPath)
				} else if err != nil {
					return err
				}
				return nil
			}

			if info.Mode()&os.ModeSymlink != 0 {
				target, err := filepath.EvalSymlinks(path)
				if err != nil {
					log.Printf("WARN: Couldn't evaluate symbolic links for %v: %v", path, err)
				}
				info, err = os.Lstat(target)
				if err != nil {
					log.Printf("WARN: Couldn't stat target %v: %v", target, err)
				}
				path = target
			}
			if info.IsDir() {
				folders = append(folders, path)
			}

			return nil
		})
		if err != nil {
			return folders, fmt.Errorf("Couldn't walk path %q: %v", mibPath, err)
		}
	}
	return folders, nil
}


func parseFile(path string, inFile string)(string, error){

	//var outFileStub = (strings.Split(inFile, "."))[0]
	//var outFile = outFileStub + ".json"

	module, err := parser.ParseFile(path + "/" + inFile)
	if err != nil {
		//log.Printf("ERROR: %v", err)
		return "", err
	}
	_ = module
	//repr.Println(module)

	// we can use the json.Marhal function to
	// encode the pigeon variable to a JSON string
	data, err := json.Marshal(module)
	// data is the JSON string represented as bytes
    if err != nil {
		log.Printf("ERROR: %v", err)
        fmt.Println(err)
        return "", err
    }

	// to print the data, we can typecast it to a string
	// log.Printf("INFO: Writing to %v", outFile)
	// fmt.Println(outFileStub + ":" + string(data) + ",")
	return string(data), nil

}

func writeFile (data string)(error){
	fmt.Println(data)
	return nil
}

func check(e error) {
    if e != nil {
        panic(e)
    }
}



func main() {
	//fmt.Println("Running loader")
	f := []string{}
	f = append(f, "../mibs")

	LoadMibsFromPath(f)
	// //fmt.Println("Running parser")
	// module, err := parser.ParseFile(os.Args[1])
	// if err != nil {
	// 	log.Fatalln(err)
	// }
	// _ = module
	// //repr.Println(module)

	// // we can use the json.Marhal function to
	// // encode the pigeon variable to a JSON string
	// data, err := json.Marshal(module)
	// // data is the JSON string represented as bytes
    // if err != nil {
    //     fmt.Println(err)
    //     return
    // }

	// // to print the data, we can typecast it to a string
	// fmt.Println(string(data))

}
